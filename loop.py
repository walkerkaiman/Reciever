import time

# Global variables (if needed)
position = 0  # Tracks the current LED position
FRAME_DELAY = 0.02  # Delay between updates

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
    position = (position + 1) % len(pixels)

    # Small delay to control animation speed
    time.sleep(FRAME_DELAY)
