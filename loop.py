"""
This module defines the behavior for 'loop' mode.
It can include sensor readings (using RPi.GPIO, for example) and applies
an LED chase animation across multiple universes. Each universe’s animation
is tracked independently.
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
      led_universes (dict): Dictionary where keys are universe numbers and values
                            are dicts containing at least the 'pixels' key.
                            
    For each universe, this function:
      - Initializes an independent animation position.
      - Clears the LED strip.
      
    You can also initialize GPIO sensors here if needed.
    """
    global positions
    positions = {}  # Reset positions for each universe.
    for key, uni in led_universes.items():
        num_pixels = len(uni["pixels"])
        # Initialize position with an offset based on the universe number
        positions[key] = key % num_pixels if num_pixels > 0 else 0
        uni["pixels"].fill((0, 0, 0))
        uni["pixels"].show()
    print("Loop mode setup complete with independent positions for each universe.")

def update(led_universes):
    """
    Called repeatedly while in 'loop' mode.
    
    For each universe, this function:
      - Clears the LED strip.
      - Lights one LED (white) at the current position.
      - Updates the position tracker for that universe.
      - Displays the updated frame.
      
    A delay is applied at the end to control the animation speed.
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
        
        # Display the update.
        pixels.show()
        
        # Update the position for the next frame for this universe.
        num_pixels = len(pixels)
        positions[key] = (pos + 1) % num_pixels if num_pixels > 0 else 0

    # Delay to control animation speed.
    time.sleep(1 / FPS)
