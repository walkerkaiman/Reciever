import sacn
import time
import random
from pynput import keyboard

num_pixels = 512
sendDMX = False

def random_rgb_color():
	r = random.randint(0, 255)
	g = random.randint(0, 255)
	b = random.randint(0, 255)
	return (r, g, b)

# same as the key press callback, but for releasing keys
def on_key_release(key):
	pass

def on_key_press(key):
	if hasattr(key, "char") and key.char == "1":
		dmx_data = []

		for i in range(num_pixels):
			dmx_data.append(random.randint(0,255))

		sender[universe_id].dmx_data = tuple(dmx_data)
		print("DMX Sent!")

	if hasattr(key, "char") and key.char == "0":
		dmx_data = []

		dmx_data = (0, ) * num_pixels

		sender[universe_id].dmx_data = tuple(dmx_data)
		print("DMX Sent!")
		#print(dmx_data)

# Initialize the sACN sender
sender = sacn.sACNsender()
sender.start()

# Activate an output universe
universe_id = 1
sender.activate_output(universe_id)

# Configure the universe
#sender[universe_id].multicast = True
sender[universe_id].destination = "192.168.4.84" # Optional: Set unicast destination

keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.start()

print("DMX Sender Started...")

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