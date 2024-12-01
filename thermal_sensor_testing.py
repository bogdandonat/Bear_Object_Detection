import time
import board
import busio
import adafruit_mlx90640

def initialize_sensor():
    """Initialize the MLX90640 sensor using Adafruit CircuitPython library."""
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)  # Create I2C bus
    mlx = adafruit_mlx90640.MLX90640(i2c)  # Initialize the sensor

    # Set refresh rate
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ

    return mlx

def main():
    print("Initializing the MLX90640 sensor...")
    try:
        sensor = initialize_sensor()
        print("Sensor initialized successfully!")

        while True:
            print("Reading thermal data...")
            frame = [0] * 768  # MLX90640 outputs 768 temperature values (24x32)
            try:
                sensor.getFrame(frame)
                max_temp = max(frame)  # Get the maximum temperature
                print(f"Maximum temperature: {max_temp:.2f}°C")  # Print the max temperature
            except Exception as e:
                print(f"Error reading frame: {e}")

            time.sleep(0.125)  # Match the refresh rate
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"Failed to initialize the sensor: {e}")

if __name__ == "__main__":
    main()
