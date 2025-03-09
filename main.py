import sacn
import time
import board
import neopixel
import sys
import threading
import queue
import socket
import os
import importlib.util
import json

# Load configuration from config.json
with open("config.json", "r") as f:
    config = json.load(f)

UDP_PORT = config.get("udp_port", 5000)
LOOP_FILE = config.get("loop_file", "loop.py")

# Initialize sACN Receiver
receiver = sacn.sACNreceiver()
receiver.start()

PIN_LOOKUP = { # Only pins possible for NeoPixels on the Raspberry Pi
    "GPIO10": board.D10,
    "GPIO12": board.D12, # PWM
    "GPIO18": board.D18,  # PWM
    "GPIO21": board.D21
}

# Dictionary to hold LED strip objects and update queues per universe
universes = {}

for universe_config in config["universes"]:
    universe_num = universe_config.get("universe", 1)
    brightness = universe_config.get("brightness", 1.0)
    num_channels = universe_config.get("channels_per_universe", 512)
    
    universes[universe_num] = {
        "pixels": neopixel.NeoPixel(PIN_LOOKUP[universe_config["data_pin"]], num_channels, brightness=brightness, auto_write=False),
        "update_queue": queue.Queue()
    }

# State tracking
current_state = "loop"
last_state = "loop"

# Load external loop module if available
def load_external_loop_module():
    global external_loop_module
    module_name = "external_loop"
    module_path = os.path.join(os.path.dirname(__file__), LOOP_FILE)
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        external_loop_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external_loop_module)
        if hasattr(external_loop_module, "setup"):
            for universe in universes.values():
                external_loop_module.setup(universe["pixels"])
        print("Loaded external loop module.")
    else:
        print("No external loop module found.")
        external_loop_module = None

load_external_loop_module()

# Handle sACN packets dynamically for each universe
def create_sacn_callback(universe_num):
    def callback(packet):
        if current_state != "show":
            return
        if not packet.dmxData:
            return
        dmx = list(packet.dmxData)
        universes[universe_num]["update_queue"].put(dmx)
    return callback

for universe_num in universes.keys():
    receiver.listen_on('universe', universe=universe_num)(create_sacn_callback(universe_num))

# UDP listener for state changes
def udp_listener():
    global current_state
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    print(f"UDP listener started on port {UDP_PORT}")
    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode('utf-8').strip().lower()
        if message in ["show", "loop"]:
            current_state = message
            print(f"State switched to: {current_state}")
            if current_state == "loop":
                for universe in universes.values():
                    while not universe["update_queue"].empty():
                        universe["update_queue"].get_nowait()

# Update LEDs based on state
def update_leds():
    global last_state, current_state
    if last_state != current_state:
        for universe in universes.values():
            universe["pixels"].fill((0, 0, 0))
            universe["pixels"].show()
        last_state = current_state

    if current_state == "show":
        for universe_num, universe in universes.items():
            latest_data = None
            while not universe["update_queue"].empty():
                latest_data = universe["update_queue"].get_nowait()
            if latest_data:
                for i in range(0, len(latest_data), 3):
                    if i // 3 < len(universe["pixels"]):
                        universe["pixels"][i // 3] = tuple(latest_data[i:i+3])
                universe["pixels"].show()
    elif current_state == "loop":
        if external_loop_module and hasattr(external_loop_module, "update"):
            for universe in universes.values():
                external_loop_module.update(universe["pixels"])

if __name__ == '__main__':
    threading.Thread(target=udp_listener, daemon=True).start()
    try:
        while True:
            update_leds()
            if current_state == "show":
                time.sleep(0.01)
    except KeyboardInterrupt:
        for universe in universes.values():
            universe["pixels"].fill((0, 0, 0))
            universe["pixels"].show()
        print("\nExiting...")
