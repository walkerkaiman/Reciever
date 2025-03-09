"""
GPIO Operations:
Reading sensor values via libraries like RPi.GPIO or gpiozero is generally fast. 
If you keep these operations optimized (for example, avoid long blocking calls), 
they should not delay the LED updates significantly.

Best Practices:
Ensure that the update function in loop.py returns quickly. 
If a sensor read or any GPIO operation takes too long, you might notice a lag in your LED animations. 
Also, if using RPi.GPIO, remember to call GPIO.cleanup() when needed (typically on exit) 
to avoid resource conflicts.
"""
import time
import RPi.GPIO

# Global variables (if needed)
position = 0  # Tracks the current LED position
FRAME_DELAY = 0.01  # Delay between updates

def setup(pixels):
    """
    This function is called once when 'loop' mode starts.
    Use it for initialization (e.g., setting up variables or clearing LEDs).
    """
    global position
    position = 0  # Reset the animation position
    pixels.fill((0, 0, 0))  # Turn off all LEDs initially
    pixels.show()

def update(pixels):
    """
    This function is called repeatedly while in 'loop' mode.
    It updates the LED animation frame-by-frame.
    """
    global position

    # Turn off all LEDs
    pixels.fill((0, 0, 0))

    # Set the current LED to white
    pixels[position] = (255, 255, 255)

    # Show the updated frame
    pixels.show()

    # Move to the next LED position
    position = (position + 1) % len(pixels-1)

    # Small delay to control animation speed
    time.sleep(FRAME_DELAY)
