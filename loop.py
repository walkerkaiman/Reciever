"""
This module defines the behavior for 'loop' mode.
It includes sensor readings using RPi.GPIO and applies an LED animation
across multiple universes, with each universe tracking its own animation position.

If a RuntimeError occurs during pixels.show() (such as a memory allocation issue),
the code will reinitialize that universe's LED strip using stored parameters.
"""

import time
import RPi.GPIO  # For sensor or input operations
import neopixel

# Dictionary to track the current position for each universe.
positions = {}
FPS = 30  # Frames per second (controls animation speed)

def setup(led_universes):
    """
    Called once when 'loop' mode starts.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
                            are dicts containing at least the 'pixels' key and initialization parameters.
                            
    Initializes an independent animation position for each universe and clears all LED strips.
    """
    global positions
    positions = {}
    for key, uni in led_universes.items():
        num_pixels = len(uni["pixels"])
        positions[key] = key % num_pixels if num_pixels > 0 else 0
        uni["pixels"].fill((0, 0, 0))
        try:
            uni["pixels"].show()
        except RuntimeError as e:
            print(f"Setup error in universe {key}: {e}")
    print("Loop mode setup complete with independent positions for each universe.")

def update(led_universes):
    """
    Called repeatedly while in 'loop' mode.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
                            are dicts containing at least the 'pixels' key and initialization parameters.
    
    For each universe:
      - Clears the LED strip.
      - Lights one LED (white) at the current position.
      - Updates the position tracker.
      - Calls pixels.show() to update the hardware.
    
    If pixels.show() raises a RuntimeError, the LED strip is reinitialized using stored parameters.
    """
    global positions
    for key, uni in led_universes.items():
        pixels = uni["pixels"]
        # Clear the LED strip.
        pixels.fill((0, 0, 0))
        
        # Get the current position for this universe.
        pos = positions.get(key, 0)
        
        # Light the LED at the current position.
        if len(pixels) > 0:
            pixels[pos] = (255, 255, 255)
        
        # Attempt to update the LEDs.
        try:
            pixels.show()
        except RuntimeError as e:
            print(f"Error updating universe {key}: {e}. Reinitializing LED strip.")
            # Reinitialize the pixels object using stored parameters.
            data_pin = uni["data_pin"]
            num_leds = uni["num_leds"]
            brightness = uni["brightness"]
            uni["pixels"] = neopixel.NeoPixel(data_pin, num_leds, brightness=brightness, auto_write=False)
            # Update the reference for this universe.
            pixels = uni["pixels"]
            # Redraw the current frame.
            pixels.fill((0, 0, 0))
            pixels[pos] = (255, 255, 255)
            try:
                pixels.show()
            except RuntimeError as err:
                print(f"Reinitialization failed in universe {key}: {err}")
        
        # Update the position for the next frame.
        num_pixels = len(pixels)
        positions[key] = (pos + 1) % num_pixels if num_pixels > 0 else 0

    # Delay to control the animation speed.
    time.sleep(1 / FPS)
