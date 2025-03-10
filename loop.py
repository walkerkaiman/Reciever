"""
This module defines the behavior for 'loop' mode.
It includes sensor readings using RPi.GPIO and applies an LED animation
across multiple universes, with each universe tracking its own animation position.
"""

import time
#import RPi.GPIO  # For sensor or input operations
#import neopixel

def setup(led_universes):
    """
    Called once when 'loop' mode starts.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
      are dicts containing at least the 'pixels' key and initialization parameters.
                            
    Initializes an independent animation position for each universe and clears all LED strips.
    """

    for key, uni in led_universes.items():
        num_pixels = uni["num_leds"]
        uni["pixels"].fill((0, 0, 0))
        
        try:
            uni["pixels"].show()
        except RuntimeError as e:
            print("Setup error in loop script!")

# Dictionary to track the current position for each universe.
positions = [0, 0, 0]

def update(led_universes):
    """
    Called repeatedly while in 'loop' mode.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
                            are dicts containing at least the 'pixels' key and initialization parameters.
    """
    global positions

    for key, uni in led_universes.items():
        # Ensure the strip is cleared before updating
        uni["pixels"].fill((0, 0, 0))

        # Light up the moving LED
        uni["pixels"][positions[key-1]] = (100, 150, 255)
        positions[key-1] = (positions[key-1] + 1) % uni["num_leds"]
        
        try:
            uni["pixels"].show()
        except RuntimeError as e:
            print(f"Error updating universe {key}: {e}")