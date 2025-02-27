import argparse
import numpy as np
import csv
import noise
import random
import math

# Generate RGB values for a frame using different techniques
def generate_frame(animation_type, num_channels, frame_idx, num_frames):
    time_factor = frame_idx / num_frames  # Normalize time between 0 and 1
    if animation_type == "sparkle":
        return generate_sparkle_frame(num_channels, time_factor)
    elif animation_type == "perlin_noise":
        return generate_perlin_noise_frame(num_channels, time_factor)
    elif animation_type == "gradient":
        return generate_gradient_frame(num_channels, time_factor)
    else:
        return generate_random_frame(num_channels)

# Random frame (basic random RGB values for each channel)
def generate_random_frame(num_channels):
    return [random.randint(0, 255) for _ in range(num_channels)]

# Sparkle effect: A few random channels get bright RGB values, but with Z-space movement
def generate_sparkle_frame(num_channels, time_factor):
    frame = [0] * num_channels
    num_sparkles = random.randint(1, 10)  # Random number of sparkles
    for _ in range(num_sparkles):
        channel = random.randint(0, num_channels - 1)
        # Use time_factor to simulate slow movement (shift over time)
        frame[channel] = random.randint(200, 255) * (math.sin(time_factor * 2 * math.pi) + 1) / 2  # Smooth modulation
    return frame

# Perlin Noise: Smooth noise for gradual transitions, with Z-space movement
def generate_perlin_noise_frame(num_channels, time_factor):
    frame = []
    for i in range(num_channels):
        noise_value = noise.pnoise1((i + time_factor * 100) / 100.0, octaves=1, persistence=0.5, lacunarity=2.0)
        frame.append(int((noise_value + 1) * 127))  # Normalize to range [0, 255]
    return frame

# Gradient: Smooth transition from one color to another, with Z-space movement
def generate_gradient_frame(num_channels, time_factor):
    frame = []
    for i in range(num_channels):
        # Simple gradient based on channel position, and time_factor moves the gradient
        color_value = int(((math.sin((i + time_factor * 100) / num_channels * math.pi * 2) + 1) * 127))
        frame.append(color_value)
    return frame

# Create the CSV file with animation data
def create_csv(animation_name, num_frames, animation_type, num_channels):
    filename = f"{animation_name}_{num_frames}_frames.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the frames
        for frame_idx in range(num_frames):
            frame = generate_frame(animation_type, num_channels, frame_idx, num_frames)
            writer.writerow(frame)
    
    print(f"CSV file created: {filename}")

# Main function to handle arguments
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a DMX light animation in CSV format.")
    parser.add_argument("animation_name", help="Name of the animation")
    parser.add_argument("num_frames", type=int, help="Number of frames in the animation")
    parser.add_argument("animation_type", choices=["sparkle", "perlin_noise", "gradient", "random"], 
                        help="Type of animation to generate")
    parser.add_argument("--num_channels", type=int, default=512, 
                        help="Number of DMX channels (default is 512)")

    # Parse arguments
    args = parser.parse_args()

    # Call function to create CSV with provided parameters
    create_csv(args.animation_name, args.num_frames, args.animation_type, args.num_channels)

# Run the main function if script is executed directly
if __name__ == "__main__":
    main()
