import smbus
import time

# Constants
VDD = 5.0  # Fixed 5V supply from Raspberry Pi to ADS1115
VOLTAGE_DIVIDER_R1 = 2000  # Resistance of R1 in ohms
VOLTAGE_DIVIDER_R2 = 1000  # Resistance of R2 in ohms
MAX_BATTERY_VOLTAGE = 13.8  # Fully charged battery voltage
MIN_BATTERY_VOLTAGE = 10.5  # Minimum battery voltage
ADS1115_ADDRESS = 0x48  # I2C address of ADS1115

# Set up I2C (bus 3)
bus = smbus.SMBus(3)

# Variables for hysteresis and last known percentage
last_percentage = None
hysteresis_threshold = 0.05  # Voltage change threshold for percentage update 50mV

def configure_ads1115(channel=0):
    """
    Configures the ADS1115 to read from a specified channel (A0-A3).
    """
    config = {
        0: [0x83, 0xE0],  # A0 
    }
    if channel in config:
        bus.write_i2c_block_data(ADS1115_ADDRESS, 0x01, config[channel])
    else:
        raise ValueError("Invalid ADS1115 channel. Choose between 0 and 3.")

def read_raw_ads1115():
    """
    Reads raw data from the ADS1115.
    """
    try:
        # Read the result (2 bytes)
        data = bus.read_i2c_block_data(ADS1115_ADDRESS, 0x00, 2)
        raw_data = (data[0] << 8) | data[1]
        if raw_data > 32767:  # Convert to signed 16-bit
            raw_data -= 65536
        return raw_data
    except Exception as e:
        print(f"Error reading ADS1115: {e}")
        return None

def convert_to_battery_voltage(raw_data):
    """
    Converts raw ADS1115 data to a battery voltage using the adjusted ±6.144V PGA range.
    """
    if raw_data is None:
        return None
    # Adjust for ±6.144V range
    measured_voltage = (raw_data / 32767.0) * 6.144

    # Adjust for voltage divider
    battery_voltage = measured_voltage * (VOLTAGE_DIVIDER_R1 + VOLTAGE_DIVIDER_R2) / VOLTAGE_DIVIDER_R2
    return battery_voltage

def battery_percentage(battery_voltage):
    """
    Calculates battery percentage from the battery voltage with hysteresis.
    """
    if battery_voltage is None:
        return None
    
    # Calculate the new percentage
    percentage = ((battery_voltage - MIN_BATTERY_VOLTAGE) / (MAX_BATTERY_VOLTAGE - MIN_BATTERY_VOLTAGE)) * 100
    percentage = max(0, min(100, percentage))  # Ensure it stays between 0 and 100
    
    # Apply hysteresis: only update percentage if the voltage change is significant enough
    global last_percentage
    if last_percentage is None:
        last_percentage = percentage
        return last_percentage
    
    # If the percentage change is smaller than the threshold, don't update it
    if abs(percentage - last_percentage) < 1:  # 1% tolerance for small fluctuations
        return last_percentage
    
    # Otherwise, update the percentage
    last_percentage = percentage
    return last_percentage

def moving_average(samples, N=5):
    """
    Returns the moving average of the last N samples.
    """
    if len(samples) < N:
        return sum(samples) / len(samples)  # Average all if fewer than N samples
    return sum(samples[-N:]) / N

def main():
    try:
        raw_samples = []  # List to store raw samples for averaging
        N = 5  # Number of samples for smoothing
        
        while True:
            # Configure ADS1115 to read from A0 (voltage divider output)
            configure_ads1115(channel=0)
            time.sleep(0.1)  # Allow time for conversion
            raw_data = read_raw_ads1115()
            calibration_factor = 0.99

            if raw_data is not None:
                # Add new raw data sample and compute moving average
                raw_samples.append(raw_data)
                avg_raw_data = moving_average(raw_samples, N)

                # Convert raw ADC value to battery voltage
                battery_voltage = convert_to_battery_voltage(avg_raw_data)
                battery_voltage *= calibration_factor

                if battery_voltage is not None:
                    # Calculate battery percentage with hysteresis
                    percentage = battery_percentage(battery_voltage)
                    print(f"Battery Voltage: {battery_voltage:.2f} V | Charge: {percentage:.2f}%")
                else:
                    print("Failed to calculate battery voltage.")
            else:
                print("Error reading ADC data.")

            time.sleep(1)  # Polling interval

    except KeyboardInterrupt:
        print("\nExiting")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
