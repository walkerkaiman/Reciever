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

# -----------------------------------------------------------------------------
# Load configuration from config.json
# -----------------------------------------------------------------------------
with open("config.json", "r") as f:
    config = json.load(f)

UDP_PORT = config.get("udp_port", 5000)
LOOP_FILE = config.get("loop_file", "loop.py")
FRAME_RATE = 30

PIN_LOOKUP = {
    "GPIO18": board.D18,
    "GPIO12": board.D12,
    "GPIO21": board.D21
}

# -----------------------------------------------------------------------------
# Initialize sACN Receiver
# -----------------------------------------------------------------------------
receiver = sacn.sACNreceiver()
receiver.start()

# -----------------------------------------------------------------------------
# Create a dictionary to hold LED strip objects and update queues per universe
# -----------------------------------------------------------------------------
# Each universe config should define:
#   - "brightness"
#   - "channels_per_universe"
#   - "universe" (number)
#   - "data_pin" (string, e.g., "GPIO18")
#   - "channels_per_fixture"
universes = {}

for uni_config in config["universes"]:
    universe_num = uni_config["universe"]
    data_pin = PIN_LOOKUP[uni_config["data_pin"]]
    brightness = uni_config.get("brightness", 1.0)
    channels_per_universe = uni_config.get("channels_per_universe", 512)
    num_leds = channels_per_universe

    universes[universe_num] = {
        "pixels": neopixel.NeoPixel(data_pin, num_leds, brightness=brightness, auto_write=False),
        "update_queue": queue.Queue(),
        "data_pin": data_pin,
        "num_leds": num_leds,
        "brightness": brightness
    }

    print(f"Initialized universe: {universe_num} NeoPixel ID: {id(universes[universe_num]['pixels'])} Pin: {data_pin} Num of LEDs: {num_leds} Brightness: {brightness}")

# -----------------------------------------------------------------------------
# Global state variable for mode ("loop" or "show")
# -----------------------------------------------------------------------------
current_state = "loop"
last_state = "loop"

# -----------------------------------------------------------------------------
# Load external loop module if available.
# -----------------------------------------------------------------------------
def load_external_loop_module():
    global external_loop_module, universes

    module_name = "external_loop"
    module_path = os.path.join(os.path.dirname(__file__), LOOP_FILE)
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        external_loop_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external_loop_module)

        if hasattr(external_loop_module, "setup"):
            external_loop_module.setup(universes)
        print("Loaded external loop module from:", module_path)
    else:
        print("No external loop module found at:", module_path)
        external_loop_module = None

load_external_loop_module()

# -----------------------------------------------------------------------------
# sACN Callback: Create a callback function per universe
# -----------------------------------------------------------------------------
def create_sacn_callback(universe_num):
    def callback(packet):
        if current_state != "show":
            return  # Only process DMX packets in "show" mode.
        if not packet.dmxData:
            return
        dmx = list(packet.dmxData)
        universes[universe_num]["update_queue"].put(dmx)
    return callback

# Register a callback for each universe.
for universe_num in universes.keys():
    receiver.listen_on('universe', universe=universe_num)(create_sacn_callback(universe_num))

# -----------------------------------------------------------------------------
# UDP Listener to switch states ("show" or "loop")
# -----------------------------------------------------------------------------
def udp_listener():
    global current_state
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    print("UDP listener started on port", UDP_PORT)
    
    while True:
        data, _ = sock.recvfrom(1024)
        message = data.decode("utf-8").strip().lower()
        
        if message in ["show", "loop"]:
            current_state = message
            print("State switched to:", current_state)
            
            # Flush DMX queues when switching to loop mode.
            if current_state == "loop":
                for uni in universes.values():
                    while not uni["update_queue"].empty():
                        uni["update_queue"].get_nowait()
        else:
            print("Received unknown command:", message)

# -----------------------------------------------------------------------------
# Command-line spinner for visual feedback
# -----------------------------------------------------------------------------
def command_line_animation():
    frames = "|/-\\"
    i = 0
    while True:
        time.sleep(0.1)
        sys.stdout.write("\r" + frames[i % len(frames)] + " Current state: " + current_state + "   ")
        sys.stdout.flush()
        i += 1

# -----------------------------------------------------------------------------
# LED Update Routine
# -----------------------------------------------------------------------------
def update_leds():
    global last_state, current_state, universes
    
    # On state change, clear all LED strips.
    if last_state != current_state:
        for uni in universes.values():
            uni["pixels"].fill((0, 0, 0))
            uni["pixels"].show()
        last_state = current_state

    if current_state == "show":
        # Process incoming DMX data for each universe.
        for uni in universes.values():
            latest_data = None
            while not uni["update_queue"].empty():
                latest_data = uni["update_queue"].get_nowait()
            if latest_data:
                # Assume each LED requires 3 channels (RGB).
                for i in range(0, len(latest_data), 3):
                    led_index = i // 3
                    if led_index < len(uni["pixels"]):
                        uni["pixels"][led_index] = tuple(latest_data[i:i+3])
                uni["pixels"].show()
    elif current_state == "loop":
        # In loop mode, delegate update to the external loop module if available.
        if external_loop_module and hasattr(external_loop_module, "update"):
            external_loop_module.update(universes)
        else:
            # Fallback: simple animation (a shifting white dot) per universe.
            for uni in universes.values():
                num_pixels = len(uni["pixels"])
                uni["pixels"].fill((0, 0, 0))
                pos = int(time.time() * 10) % num_pixels
                uni["pixels"][pos] = (255, 255, 255)
                uni["pixels"].show()
                print("No loop file found. Make sure it exists and correctly assigned in config.json.")

if __name__ == '__main__':
    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=command_line_animation, daemon=True).start()
    try:
        while True:
            update_leds()
            time.sleep(1 / FRAME_RATE)
    except KeyboardInterrupt:
        for uni in universes.values():
            uni["pixels"].fill((0, 0, 0))
            uni["pixels"].show()
        print("\nExiting...")
