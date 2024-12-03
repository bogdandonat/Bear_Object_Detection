import os
import time
import threading
import cv2
from queue import Queue
from camera_test import setup_mqtt_client, capture_and_send_images, listen
from relay_control import relay_setup, turn_off_relay, turn_on_relay
from thermal_sensor_testing import ThermalSensor

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
relay_state = False
image_queue = Queue()

# Event to trigger relay from MQTT messages
relay_trigger_event = threading.Event()

def handle_message(payload):
    """Handles the MQTT message and triggers the relay."""
    if payload == "Trigger relay":
        turn_on_relay(RELAY_PIN_1, RELAY_PIN_2)
        relay_trigger_event.set()  
    elif payload == "Turn off relay":
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
        relay_trigger_event.clear()  
    else:
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
        relay_trigger_event.clear()  

def start_listener():
    """Starts the MQTT listener in a separate thread."""
    listen(MQTT_BROKER, MQTT_PORT, MQTT_SUBSCRIBE_TOPIC, handle_message)

def save_images():
    """Save images from the queue in a separate thread."""
    while True:
        if not image_queue.empty():
            image, timestamp = image_queue.get()
            image_path = os.path.join(IMAGE_FOLDER, f"image_{timestamp}.jpg")
            print(f"Saving image to: {image_path}")
            cv2.imwrite(image_path, image)  

def capture_images():
    """Capture images and add them to the queue continuously."""
    client = setup_mqtt_client(MQTT_BROKER, MQTT_PORT)
    while True:
        # Capture the image 
        image = capture_and_send_images(client, MQTT_PUBLISH_TOPIC, IMAGE_FOLDER)
        timestamp = int(time.time() * 1000)  
        image_queue.put((image, timestamp))  

def read_temperature():
    """Read the temperature continuously in a separate thread."""
    global max_temp, max_allowed_temp
    thermal_sensor = ThermalSensor()
    while True:
        try:
            max_temp, max_allowed_temp = thermal_sensor.read_temperature()
            if max_temp is not None and max_allowed_temp is not None:
                print(f"Maximum temp: {max_temp:.2f} °C, Max Allowed Temp: {max_allowed_temp} °C")
            else:
                print("Temperature data is not available")
        except Exception as e:
            print(f"Error reading temperature : {e}")
            max_temp, max_allowed_temp = None, None
        time.sleep(1)

def control_relay():
    """Relay control based on temperature in a separate thread."""
    global relay_state
    while True:
        if max_temp > max_allowed_temp and not relay_state:
            turn_on_relay(RELAY_PIN_1, RELAY_PIN_2)
            relay_state = True
        elif max_temp < max_allowed_temp and relay_state:
            turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
            relay_state = False
        time.sleep(1)

def main():
    # Initialize MQTT client, relays, and thermal sensor
    print("Initializing MQTT client...")
    client = setup_mqtt_client(MQTT_BROKER, MQTT_PORT)

    print("Initializing relays...")
    relay_setup(RELAY_PIN_1, RELAY_PIN_2)

    print("Starting MQTT listener in a separate thread...")
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    print("Starting image saving in a separate thread...")
    save_thread = threading.Thread(target=save_images, daemon=True)
    save_thread.start()

    print("Starting image capture in a separate thread...")
    capture_thread = threading.Thread(target=capture_images, daemon=True)
    capture_thread.start()

    print("Starting temperature reading in a separate thread...")
    temp_thread = threading.Thread(target=read_temperature, daemon=True)
    temp_thread.start()

    print("Starting relay control in a separate thread...")
    relay_thread = threading.Thread(target=control_relay, daemon=True)
    relay_thread.start()

    print("All peripherals and sensors are initialized. Starting main loop...")

    # Main loop to handle relay trigger based on MQTT
    try:
        while True:
            if relay_trigger_event.is_set():
                print("Relay triggered by MQTT message.")
            else:
                print("Relay not triggered by MQTT.")
            time.sleep(1)  # Allow enough time for the listener and other threads to process messages
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        turn_off_relay(RELAY_PIN_1, RELAY_PIN_2)
        print("Cleaned up and shutting down.")

if __name__ == "__main__":
    main()
