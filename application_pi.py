from camera_test import setup_mqtt_client, capture_and_send_images, listen
from relay_control import relay_setup, turn_off_relay, turn_on_relay
from thermal_sensor_testing import initialize_sensor
import threading
import time
from datetime import datetime

# Configuration
MQTT_BROKER = "192.168.0.140"
MQTT_PORT = 1883
MQTT_PUBLISH_TOPIC = "camera/images"
MQTT_SUBSCRIBE_TOPIC = "response/trigger"
IMAGE_FOLDER = "/home/bogdan/images"
RELAY_PIN_1 = 17  # Alarm pin
RELAY_PIN_2 = 27  # LED pin

# Global Variables
max_temp = 0
max_allowed_temp = 0

def handle_message(payload):
   
    if payload == "Trigger relay":
        turn_on_relay(RELAY_PIN_1, RELAY_PIN_2)
    elif payload == "Turn off relay":
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
    else:
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)

def start_listener():
   
    listen(MQTT_BROKER, MQTT_PORT, MQTT_SUBSCRIBE_TOPIC, handle_message)

def main():
    # Initialize MQTT client, relays, and thermal sensor
    print("Initializing MQTT client...")
    client = setup_mqtt_client(MQTT_BROKER, MQTT_PORT)

    print("Initializing relays...")
    relay_setup(RELAY_PIN_1, RELAY_PIN_2)

    print("Initializing thermal sensor...")
    thermal_sensor = initialize_sensor()

    print("Starting MQTT listener...")
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    print("All peripherals and sensors are initialized. Starting main loop...")
    try:
        while True:
            # Capture and send images
            capture_and_send_images(client, MQTT_PUBLISH_TOPIC, IMAGE_FOLDER)

            # Read temperature
            global max_temp, max_allowed_temp
            max_temp, max_allowed_temp = thermal_sensor.read_temperature()
            print(f"Maximum temp: {max_temp:.2f} °C, Max Allowed Temp: {max_allowed_temp} °C")

            # Relay control based on temperature
            if max_temp > max_allowed_temp:
                turn_on_relay(RELAY_PIN_1, RELAY_PIN_2)
            else:
                turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)

            time.sleep(0.125)  # Adjust based on thermal sensor refresh rate
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
        print("Cleaned up and shutting down.")

if __name__ == "__main__":
    main()
