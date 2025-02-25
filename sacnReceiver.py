import sacn
import time
import board
import neopixel
import sys
import threading
import queue
import socket

# Command-line spinner frames.
command_line_animation_frames = "|/-\\"

# Global state variable; default is "stream"
current_state = "stream"
last_state = "stream"  # used to detect state changes

# Initialize the LED strip (adjust the pixel count as needed)
pixels = neopixel.NeoPixel(board.D18, 300, brightness=0.3, auto_write=False)
update_queue = queue.Queue()

# Initialize and start the sACN receiver.
receiver = sacn.sACNreceiver()
receiver.start()

@receiver.listen_on('universe', universe=1)
def callback(packet):
    """
    Only process DMX data when in "stream" mode.
    Convert incoming DMX data into RGB groups and enqueue.
    """
    if current_state != "stream":
        return  # ignore DMX data when not streaming
    if not packet.dmxData or len(packet.dmxData) < 3:
        return
    dmx = list(packet.dmxData)
    groups = len(dmx) - (len(dmx) % 3)
    pixel_data = [dmx[i:i+3] for i in range(0, groups, 3)]
    update_queue.put(pixel_data)

def udp_listener():
    """
    Listen on UDP (port 5005) for messages ("stream" or "loop")
    to change state. When switching to "loop", flush any queued DMX data.
    """
    global current_state
    udp_ip = "0.0.0.0"  # Listen on all interfaces.
    udp_port = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    print("UDP listener started on {}:{}".format(udp_ip, udp_port))
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8').strip().lower()
        if message in ["stream", "loop"]:
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

# Variable to drive our loop animation.
loop_animation_index = 0

def update_leds():
    """
    Update the LED strip based on the current state.
    
    In "stream" mode:
      - Pull DMX data from the update_queue and update the LEDs.
      
    In "loop" mode:
      - Run a simple shifting animation.
      
    Also, detect state transitions to perform a reset.
    All calls to pixels.show() are executed in the main thread.
    """
    global loop_animation_index, last_state, current_state

    # Detect state change and perform a reset if needed.
    if last_state != current_state:
        # Clear any residual data and reset the LED strip.
        pixels.fill((0, 0, 0))
        pixels.show()
        last_state = current_state

    if current_state == "stream":
        try:
            pixel_data = update_queue.get(timeout=0.01)
            for i, color in enumerate(pixel_data):
                if i < len(pixels):
                    pixels[i] = color
            pixels.show()
        except queue.Empty:
            # No new DMX data available.
            pass
    elif current_state == "loop":
        num_pixels = len(pixels)
        for i in range(num_pixels):
            # Create a shifting gradient effect.
            r = (i * 5 + loop_animation_index) % 256
            g = (i * 3 + loop_animation_index * 2) % 256
            b = (i * 7 + loop_animation_index * 3) % 256
            pixels[i] = (r, g, b)
        pixels.show()
        loop_animation_index = (loop_animation_index + 1) % 256
        # Throttle updates in loop mode.
        time.sleep(0.1)

if __name__ == '__main__':
    # Start the UDP listener and command-line animation in daemon threads.
    udp_thread = threading.Thread(target=udp_listener, daemon=True)
    udp_thread.start()

    animation_thread = threading.Thread(target=command_line_animation, daemon=True)
    animation_thread.start()

    try:
        # Main loop: update LEDs from the main thread.
        while True:
            update_leds()
            # In stream mode, add a very short delay to yield CPU time.
            if current_state == "stream":
                time.sleep(0.01)
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        print("\nExiting...")
