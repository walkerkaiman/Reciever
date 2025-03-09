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

# Command-line spinner frames.
command_line_animation_frames = "|/-\\"

# Load configuration from config.json
with open("config.json", "r") as f:
    config = json.load(f)

LED_BRIGHTNESS = config.get("led_brightness", .3)
NUM_LEDS = config.get("num_leds", 300)
UNIVERSE = config.get("universe", 1)
UDP_PORT = config.get("udp_port", 5005)
LOOP_FILE = config.get("loop_file", "loop.py")

# Global state variable; default is "loop"
current_state = "loop"
last_state = "loop"  # used to detect state transitions

# Initialize the LED strip (adjust the pixel count as needed)
pixels = neopixel.NeoPixel(board.D18, NUM_LEDS, brightness=LED_BRIGHTNESS, auto_write=False)
update_queue = queue.Queue()

# =============================================================================
# Load external loop module (if available)
# =============================================================================
external_loop_module = None

def load_external_loop_module():
    global external_loop_module

    module_name = "external_loop"
    module_path = os.path.join(os.path.dirname(__file__), LOOP_FILE)

    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        external_loop_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(external_loop_module)
        
        # Optionally run a setup routine from the external module.
        if hasattr(external_loop_module, "setup"):
            external_loop_module.setup(pixels)
        external_loop_module.initialized = True
        print("Loaded external loop module from:", module_path)
    else:
        print("No external loop module found at:", module_path)
        external_loop_module = None

load_external_loop_module()

# =============================================================================
# sACN Receiver Setup
# =============================================================================
receiver = sacn.sACNreceiver()
receiver.start()

@receiver.listen_on('universe', universe=UNIVERSE)
def callback(packet):
    """
    Only process DMX data when in "show" mode.
    Convert incoming DMX data into RGB groups and enqueue.
    """
    if current_state != "show":
        return  # ignore DMX data when not in show
    if not packet.dmxData or len(packet.dmxData) < 3:
        return
    dmx = list(packet.dmxData)
    groups = len(dmx) - (len(dmx) % 3)
    pixel_data = [dmx[i:i+3] for i in range(0, groups, 3)]
    update_queue.put(pixel_data)

# =============================================================================
# UDP Listener to switch states
# =============================================================================
def udp_listener():
    """
    Listen on UDP (port 5005) for messages ("show" or "loop")
    to change state. When switching to "loop", flush any queued DMX data.
    """
    global current_state
    udp_ip = "0.0.0.0"  # Listen on all interfaces.
    udp_port = UDP_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    print("UDP listener started on {}:{}".format(udp_ip, udp_port))
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8').strip().lower()
        if message in ["show", "loop"]:
            current_state = message
            print("\nState switched to:", current_state)
            # Flush the DMX update queue when switching modes.
            if current_state == "loop":
                while not update_queue.empty():
                    try:
                        update_queue.get_nowait()
                    except queue.Empty:
                        break
        else:
            print("\nReceived unknown command:", message)

# =============================================================================
# Command-line Animation (for visual feedback)
# =============================================================================
def command_line_animation():
    """
    Display a command-line spinner with the current state.
    """
    i = 0
    while True:
        time.sleep(0.1)
        sys.stdout.write("\r" + command_line_animation_frames[i % len(command_line_animation_frames)] +
                         " Current state: " + current_state + "   ")
        sys.stdout.flush()
        i += 1

# =============================================================================
# LED Update Routine
# =============================================================================
# Variable to drive our fallback loop animation.
loop_animation_index = 0

def update_leds():
    """
    Update the LED strip based on the current state.
    
    In "show" mode:
      - Pull DMX data from the update_queue and update the LEDs.
      
    In "loop" mode:
      - If an external loop module is loaded and defines an 'update(pixels)' function,
        delegate the LED update to that function.
      - Otherwise, use a fallback simple shifting animation.
      
    Also, detect state transitions to perform a reset.
    All calls to pixels.show() are executed in the main thread.
    """
    global loop_animation_index, last_state, current_state

    # Detect state change and perform a reset if needed.
    if last_state != current_state:
        pixels.fill((0, 0, 0))
        pixels.show()
        last_state = current_state

    if current_state == "show":
        latest_data = None
        # Drain the queue; process only the most recent data.
        while not update_queue.empty():
            try:
                latest_data = update_queue.get_nowait()
            except queue.Empty:
                break
        if latest_data is not None:
            for i, color in enumerate(latest_data):
                if i < len(pixels):
                    pixels[i] = color
            pixels.show()
    elif current_state == "loop":
        if external_loop_module is not None and hasattr(external_loop_module, "update"):
            external_loop_module.update(pixels)
        else:
            num_pixels = len(pixels)
            for i in range(num_pixels):
                r = (i * 5 + loop_animation_index) % 256
                g = (i * 3 + loop_animation_index * 2) % 256
                b = (i * 7 + loop_animation_index * 3) % 256
                pixels[i] = (r, g, b)
            pixels.show()
            loop_animation_index = (loop_animation_index + 1) % 256
        time.sleep(0.1)

# =============================================================================
# Main Execution
# =============================================================================
if __name__ == '__main__':
    # Start the UDP listener and command-line spinner in daemon threads.
    udp_thread = threading.Thread(target=udp_listener, daemon=True)
    udp_thread.start()

    animation_thread = threading.Thread(target=command_line_animation, daemon=True)
    animation_thread.start()

    try:
        # Main loop: update LEDs from the main thread.
        while True:
            update_leds()
            if current_state == "show":
                time.sleep(0.01)
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        print("\nExiting...")
