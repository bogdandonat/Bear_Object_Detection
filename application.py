import os
import time
import threading
import cv2
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import numpy as np
from flask import Flask, jsonify, send_from_directory, make_response, render_template
from queue import Queue
import uuid

# Configuration
model_path = r"C:\Users\Bogdan\runs\detect\train15_v2\weights\best.pt"
image_folder = r"E:\Bear Project\dev\Bear_Object_Detection\static"
upload_folder = r"E:\Bear Project\dev\Bear_Object_Detection\upload_folder"
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_publish_topic = "response/trigger"
mqtt_subscribe_temp_topic = "sensor/temperature"
mqtt_subscribe_topic = "camera/images"
mqtt_subscribe_battery_topic = "sensor/battery"

# Create Flask app
app = Flask(__name__, static_folder="static")

# Counter and relay status
bear_counter = 0
relay_on = False
latest_image = None
latest_temperature = None
latest_battery_percentage = None

# Create folder for storing the images
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Load model
model = YOLO(model_path)

# Queue for image processing
image_queue = Queue()

# MQTT Callback for receiving messages
def on_message(client, userdata, msg):
    global bear_counter, relay_on, latest_image, latest_temperature, latest_battery_percentage
    #Message topic is image
    if msg.topic == mqtt_subscribe_topic:
    # Convert image bytes to OpenCV image
        image_np = np.frombuffer(msg.payload, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        timestamp = int(time.time() * 1000)
        image_path = os.path.join(image_folder, f"image_{timestamp}.jpg")
        cv2.imwrite(image_path, image)

    # Add image path to queue for further processing
        image_queue.put(image_path)
        latest_image = f"image_{timestamp}.jpg"

        print(f"Image received and saved: {image_path}")
    # Message topic is temperature
    elif msg.topic == mqtt_subscribe_temp_topic:
        try:
            temperature_data = eval(msg.payload.decode())
            latest_temperature = temperature_data
            print(f"Temperature data received: {latest_temperature}")
        except Exception as e:
            print(f"Error parsing temperature data: {e}")
    elif msg.topic == mqtt_subscribe_battery_topic:
        try:
            battery_percentage = float(msg.payload.decode())
            latest_battery_percentage = round(battery_percentage, 0)
            print(f"Battery percentage received: {latest_battery_percentage}%")
        except Exception as e:
            print(f"Error parsing battery percentage: {e}") 

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_subscribe_topic)
client.subscribe(mqtt_subscribe_temp_topic)
client.subscribe(mqtt_subscribe_battery_topic)

def mqtt_client():
    client.loop_forever()

# Object detection and relay control in separate thread
def process_images():
    global bear_counter, relay_on
    while True:
        if not image_queue.empty():
            image_path = image_queue.get()
            image = cv2.imread(image_path)

            # Perform object detection
            results = model(image)
            detected_bears = []

            for result in results:
                for box, conf, cls in zip(result.boxes.xywh, result.boxes.conf, result.boxes.cls):
                    if result.names[int(cls)] == 'brown_bear' and conf > 0.6:
                        detected_bears.append({
                            'x': box[0], 'y': box[1], 'width': box[2], 'height': box[3], 'confidence': conf
                        })

            # Handle bear detection and relay status
            if detected_bears:
                bear_counter += 1
                print(f"Brown bear detected! Total detections: {bear_counter}")
                if not relay_on:
                    relay_on = True
                    client.publish(mqtt_publish_topic, "Trigger relay")
            else:
                if relay_on:
                    relay_on = False
                    client.publish(mqtt_publish_topic, "Turn off relay")

        time.sleep(0.1)  # Delay to prevent excessive CPU usage

# Flask routes
@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    return response

@app.route('/images-captured/<filename>')
def send_image(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/latest-image')
def latest_image_route():
    global latest_image, bear_counter, relay_on, latest_temperature, latest_battery_percentage
    if latest_battery_percentage is not None:
        print(f"Latest battery percentage in the route: {latest_battery_percentage:.2f}")
    else:
        print("Battery percentage is not yet available")
    if latest_image:
        response = make_response(jsonify({
            'latest_image': latest_image,
            'bear_count': bear_counter,
            'relay_status': "Active" if relay_on else "Inactive",
            'temperature': latest_temperature,
            'battery_percentage': latest_battery_percentage
        }))
        return response
    else:
        return jsonify({
            'latest_image': '',  # No image yet
            'bear_count': bear_counter,
            'relay_status': "Inactive",
            'temperature': latest_temperature,
            'battery_percentage': latest_battery_percentage
        })

@app.route('/')
def index():
    global latest_image, bear_counter, relay_on, latest_temperature, latest_battery_percentage

    if latest_image:
        image_url = f"/static/{latest_image}"  
    else:
        image_url = ''
    
    return render_template("index.html", latest_image=image_url, bear_count=bear_counter, relay_status=relay_on, latest_temperature=latest_temperature, battery_percentage= latest_battery_percentage)

# Flask server
def flask_server():
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    # Separate threads for Flask server, MQTT broker, and image processing
    mqtt_thread = threading.Thread(target=mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Start image processing thread
    image_processing_thread = threading.Thread(target=process_images, daemon=True)
    image_processing_thread.start()

    # Start Flask server in the main thread
    flask_server()

if __name__ == "__main__":
    main()
