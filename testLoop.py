import time
import board
import neopixel
from noise import pnoise1
import math

# Configuration
NUM_PIXELS = 60
PIXEL_PIN = board.D18
BRIGHTNESS = 1.0
FADE_DURATION = 3.0        # Seconds for fade in and out
ANIMATION_DURATION = 10.0  # Seconds at full brightness
NOISE_SCALE = 0.1
WAVE_SPEED = 0.2

# Initialize LED strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

def get_wave_intensity(pos, t):
    wave = math.sin((pos * 0.3) - (t * WAVE_SPEED)) * 0.5 + 0.5
    noise_val = pnoise1(pos * NOISE_SCALE + t * 0.1)
    noise_val = (noise_val + 1) / 2  # Normalize to [0,1]
    return wave * noise_val

def render_frame(t, brightness=1.0):
    for i in range(NUM_PIXELS):
        intensity = get_wave_intensity(i, t) * brightness
        val = int(intensity * 255)
        pixels[i] = (val, val, val)
    pixels.show()

def fade(pixels, start_brightness, end_brightness, duration, t_start):
    steps = 60
    for step in range(steps + 1):
        interp = step / steps
        brightness = start_brightness + (end_brightness - start_brightness) * interp
        render_frame(time.time() - t_start, brightness)
        time.sleep(duration / steps)

try:
    while True:
        t_start = time.time()

        # Fade In
        fade(pixels, 0.0, 1.0, FADE_DURATION, t_start)

        # Full brightness animation
        t_loop_start = time.time()
        while time.time() - t_loop_start < ANIMATION_DURATION:
            render_frame(time.time() - t_start, brightness=1.0)
            time.sleep(0.02)

        # Fade Out
        fade(pixels, 1.0, 0.0, FADE_DURATION, time.time())

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
