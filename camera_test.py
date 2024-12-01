import time
import subprocess
import paho.mqtt.client as mqtt
import os

# Configuration
mqtt_broker = "192.168.0.140"  # Replace with the IP of your PC
mqtt_port = 1883
mqtt_publish_topic = "camera/images"
mqtt_subscribe_topic = "response/trigger"
image_folder = "/home/bogdan/images"  # Folder to save images (ensure this exists)

# Ensure the image folder exists
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Set up MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port)

# Start MQTT client loop
client.loop_start()

def capture_and_send_image():
    while True:
        # Generate a unique filename for each image
        timestamp = int(time.time() * 1000)
        image_path = os.path.join(image_folder, f"image_{timestamp}.jpg")
        
        # Capture image using libcamera (without --format option)
        result = subprocess.run(["libcamera-still", "--width", "256", "--height", "256", "-o", image_path], capture_output=True)

        if result.returncode == 0:
            print(f"Image saved: {image_path}")

            # Read the captured image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Publish image to MQTT broker
            client.publish(mqtt_publish_topic, image_data)
            print("Image sent to broker")
        else:
            print(f"Error capturing image: {result.stderr.decode()}")

        time.sleep(1 / 30)  # Wait for 1/30th of a second to simulate 30 FPS

# Capture and send images
capture_and_send_image()
