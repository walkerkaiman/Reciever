"""
This module defines the behavior for 'loop' mode.
It can include sensor readings using RPi.GPIO (or gpiozero)
and applies an LED animation across multiple universes.

Best Practices:
  - Keep the update() function non-blocking and fast.
  - If using RPi.GPIO, perform GPIO.cleanup() on exit if needed.
"""

import time
import RPi.GPIO  # For sensor or input operations

# Global variables for animation
position = 0  # Common animation position across universes
FPS = 30      # Frames per second (controls animation speed)

def setup(led_universes):
    """
    Called once when 'loop' mode starts.
    led_universes: A dictionary where keys are universe numbers and values are dicts with a 'pixels' key.
    This function initializes animation variables and clears all LED strips.
    """
    global position
    position = 0  # Reset the animation position
    for uni in led_universes.values():
        uni["pixels"].fill((0, 0, 0))
        uni["pixels"].show()
    # Example: Setup GPIO sensor(s) if needed.
    # RPi.GPIO.setmode(RPi.GPIO.BCM)
    # RPi.GPIO.setup(17, RPi.GPIO.IN)
    print("Loop mode setup complete.")

def update(led_universes):
    """
    Called repeatedly while in 'loop' mode.
    led_universes: A dictionary where keys are universe numbers and values are dicts with a 'pixels' key.
    This example performs a simple animation by lighting a single LED white on each strip.
    Sensor readings or more advanced logic can be added here.
    """
    global position
    # For each universe, perform the animation update.
    for uni in led_universes.values():
        pixels = uni["pixels"]
        # Clear the LED strip.
        pixels.fill((0, 0, 0))
        # If there are LEDs, light one LED at the current position.
        if len(pixels) > 0:
            pixels[position] = (255, 255, 255)
        pixels.show()
    
    # Update the position for the next frame.
    # This is a common position across all universes; you could also track separate positions if desired.
    # Here we assume all universes have the same number of LEDs.
    sample_universe = next(iter(led_universes.values()))
    num_pixels = len(sample_universe["pixels"])
    position = (position + 1) % num_pixels

    # Delay to control the animation speed.
    time.sleep(1 / FPS)
