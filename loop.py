"""
This module defines the behavior for 'loop' mode.
It includes sensor readings using RPi.GPIO (if needed) and applies an LED animation
across multiple universes, with each universe tracking its own animation position.
"""

import time
import RPi.GPIO  # For sensor or input operations

# Dictionary to track the current position for each universe.
positions = {}
FPS = 30  # Frames per second (controls animation speed)

def setup(led_universes):
    """
    Called once when 'loop' mode starts.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
                            are dictionaries containing at least the 'pixels' key.
    
    This function initializes a separate animation position for each universe and clears all LED strips.
    """
    global positions
    positions = {}  # Reset positions for each universe.
    for key, uni in led_universes.items():
        positions[key] = 0  # Start position at 0 for this universe.
        uni["pixels"].fill((0, 0, 0))
        uni["pixels"].show()
    # Example: Setup GPIO sensor(s) if needed.
    # RPi.GPIO.setmode(RPi.GPIO.BCM)
    # RPi.GPIO.setup(17, RPi.GPIO.IN)
    print("Loop mode setup complete with independent positions for each universe.")

def update(led_universes):
    """
    Called repeatedly while in 'loop' mode.
    
    Parameters:
      led_universes (dict): A dictionary where keys are universe numbers and values
                            are dictionaries containing at least the 'pixels' key.
    
    For each universe, this function:
      - Clears the LED strip.
      - Lights one LED (white) at the current position.
      - Updates the position tracker independently.
      - Shows the updated frame.
      
    A delay is applied at the end to control the animation speed.
    """
    global positions
    for key, uni in led_universes.items():
        pixels = uni["pixels"]
        # Clear the LED strip.
        pixels.fill((0, 0, 0))
        
        # Get the current position for this universe.
        pos = positions.get(key, 0)
        
        # If there are LEDs, light one LED at the current position.
        if len(pixels) > 0:
            pixels[pos] = (255, 255, 255)
        pixels.show()
        
        # Update the position for the next frame for this universe.
        num_pixels = len(pixels)
        positions[key] = (pos + 1) % num_pixels

    # Delay to control the animation speed.
    time.sleep(1 / FPS)
