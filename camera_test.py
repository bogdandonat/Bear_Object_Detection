import time
import subprocess
import paho.mqtt.client as mqtt
import os

def setup_mqtt_client(broker, port, on_message_callback=None):
   
    client = mqtt.Client()

    if on_message_callback:
        client.on_message = on_message_callback

    client.connect(broker, port)
    client.loop_start()
    return client

def ensure_folder_exists(folder_path):
   
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def capture_image(image_folder, width=256, height=256):
   
    timestamp = int(time.time() * 1000)
    image_path = os.path.join(image_folder, f"image_{timestamp}.jpg")

    result = subprocess.run(
        ["libcamera-still", "--width", str(width), "--height", str(height), "-o", image_path],
        capture_output=True
    )

    if result.returncode == 0:
        print(f"Image saved: {image_path}")
        return image_path
    else:
        print(f"Error capturing image: {result.stderr.decode()}")
        return None

def send_image_to_mqtt(client, topic, image_path):
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    client.publish(topic, image_data)
    print(f"Image sent to topic {topic}")

def capture_and_send_images(client, topic, image_folder, interval=1/30):
    
    ensure_folder_exists(image_folder)
    image_path = capture_image(image_folder)
    if image_path:
        send_image_to_mqtt(client, topic, image_path)
    time.sleep(interval)

def listen(broker, port, topic, handle_message):

    def on_message(client, userdata, message):
        payload = message.payload.decode()
        print(f"Received message on topic {message.topic}: {payload}")
        handle_message(payload)
    
    print("Setting up MQTT client for listening..")
    client = setup_mqtt_client(broker, port, on_message_callback=None)
    client.subscribe(topic)
    print(f"Subscribed to topic: {topic}")
    while True:
        time.sleep(1)