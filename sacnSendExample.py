import sacn
import time
import random
from pynput import keyboard
import socket

num_pixels = 512
current_state = "loop"  # initial state

# Setup a UDP socket to send state-switching commands.
udp_ip = "192.168.4.84"  # Replace with your installation's IP if different.
udp_port = 5005          # Port on which the installation's UDP listener is running.
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def random_rgb_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)

def on_key_release(key):
    pass

def on_key_press(key):
    global current_state
    if hasattr(key, "char"):
        if key.char == "1":
            if current_state == "stream":
                # Send a frame of random DMX data.
                dmx_data = []
                for i in range(num_pixels):
                    dmx_data.append(random.randint(0, 255))
                sender[universe_id].dmx_data = tuple(dmx_data)
                print("DMX Sent!")
        elif key.char == "0":
            if current_state == "stream":
                # Turn off the LEDs.
                dmx_data = (0,) * num_pixels
                sender[universe_id].dmx_data = tuple(dmx_data)
                print("DMX Sent! (LEDs Off)")
        elif key.char == "2":
            # Toggle the state between 'stream' and 'loop'
            if current_state == "stream":
                current_state = "loop"
            else:
                current_state = "stream"
            # Send the new state over UDP to the installation.
            udp_socket.sendto(current_state.encode('utf-8'), (udp_ip, udp_port))
            print("State switched to:", current_state)

# Initialize the sACN sender
sender = sacn.sACNsender()
sender.start()

# Activate an output universe
universe_id = 1
sender.activate_output(universe_id)

# Configure the universe destination (this is for DMX streaming)
sender[universe_id].destination = "192.168.4.84"  # Set to the installation's IP if needed

# Start the keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.start()

print("DMX Sender Started... (Press 1 to send DMX, 0 to turn off, 2 to toggle state)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    dmx_data = (0,) * num_pixels
    sender[universe_id].dmx_data = tuple(dmx_data)
    print("Turn off LEDs")
finally:
    sender.stop()
    keyboard_listener.stop()
    keyboard_listener.join()
    print("Closed DMX Sender")
