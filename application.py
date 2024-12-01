import os
import time
import threading
import cv2
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import numpy as np
from flask import Flask, jsonify, send_from_directory, request, make_response, render_template
import uuid

# Configuration

model_path = r"C:\Users\Bogdan\runs\detect\train15_v2\weights\best.pt"
image_folder = r"E:\Bear Project\images captured"
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_publish_topic = "response/trigger"
mqtt_subscribe_topic = "camera/images"

# Create Flask app
app = Flask(__name__, static_folder=image_folder)

# Counter and relay status
bear_counter = 0
relay_on = False
latest_image = None

# Create folder for storing the images on the mqtt broker
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Load model
model = YOLO(model_path)

# Receiving images via mqtt
def on_message(client, userdata, msg):
    global bear_counter, relay_on, latest_image

    # Convert image bytes to OpenCV image
    image_np = np.frombuffer(msg.payload, dtype=np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Save the image with a timestamped filename
    image_path = os.path.join(image_folder, f"image_{int(time.time() * 1000)}.jpg")
    cv2.imwrite(image_path, image)

    # Update latest image information
    latest_image = f"image_{int(time.time() * 1000)}.jpg"
    print(f"Image received and saved: {image_path}")

    # Perform object detection
    results = model(image)
    detected_bears = []
    for result in results:
        for box, conf, cls in zip(result.boxes.xywh, result.boxes.conf, result.boxes.cls):
            if result.names[int(cls)] == 'brown_bear' and conf > 0.8:
                detected_bears.append({
                    'x': box[0],  # x center
                    'y': box[1],  # y center
                    'width': box[2],  # width
                    'height': box[3],  # height
                    'confidence': conf,  # confidence score
                    'class': cls  # class index
                })

    # Handle bear detection and relay status
    if detected_bears:
        bear_counter += 1
        print(f"Brown bear detected! Total detections: {bear_counter}")

        # Send the response back to Raspberry Pi
        if not relay_on:
            relay_on = True
            client.publish(mqtt_publish_topic, "Trigger relay")
    else:
        if relay_on:
            relay_on = False
            client.publish(mqtt_publish_topic, "Turn off relay")

# MQTT setup
client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_subscribe_topic)

def mqtt_client():
    client.loop_forever()

# Flask routes

# Route to return the latest image and stats in JSON format
@app.route('/latest-image')
def latest_image_route():
    global latest_image, bear_counter, relay_on
    
    # Check if there's a valid latest image
    if latest_image:
        response = make_response(jsonify({
            'latest_image': latest_image,
            'bear_count': bear_counter,
            'relay_status': "Active" if relay_on else "Inactive"
        }))
        
        # Cache the response for 10 seconds
        response.headers['Cache-Control'] = 'public, max-age=10'
        
        return response
    else:
        return jsonify({
            'latest_image': '',  # No image yet, return empty string
            'bear_count': bear_counter,
            'relay_status': "Inactive"
        })

# Route to serve static images from the image folder
@app.route('/static/<filename>')
def send_image(filename):
    return send_from_directory(image_folder, filename)

@app.route('/')
def index():
    global latest_image, bear_counter, relay_on

    if latest_image:
        image_url = f"/static/{latest_image}"
    else:
        image_url = ''
    
    return render_template("index.html", latest_image=image_url, bear_count=bear_counter, relay_status=relay_on)
   

# Route to upload a new image
@app.route('/upload-image', methods=['POST'])
def upload_image():
    global latest_image, bear_counter, relay_on

    # Check if an image file was provided in the request
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    # Check if the image file is empty
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Generate a unique filename for the uploaded image (to avoid overwriting existing files)
    file_extension = image_file.filename.split('.')[-1]
    new_image_filename = str(uuid.uuid4()) + '.' + file_extension

    # Save the image to the specified directory
    image_path = os.path.join(image_folder, new_image_filename)
    image_file.save(image_path)

    # Update the latest image information
    latest_image = new_image_filename

    # Simulate bear count increment and relay status change
    bear_counter += 1  # Example increment for each new bear detected
    relay_on = True  # Example status change for the relay

    return jsonify({
        'message': 'Image uploaded successfully',
        'latest_image': latest_image
    })

def flask_server():
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    # Separate threads for Flask server and MQTT broker
    mqtt_thread = threading.Thread(target=mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    flask_server()

if __name__ == "__main__":
    main()
