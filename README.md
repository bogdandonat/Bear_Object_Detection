# Bear_Object_Detection
YOLO model for detecting brown bears on a custom dataset, deployment on MQTT server and visual input from Raspberry Pi 4, User could see the input on a webpage created with flask that is running on the same server as MQTT broker

IoT solution with ML detection against bear's attacks

The ML model will be running on a MQTT Server.

The RPi 4 will send the input to the server, if there is any bear, the server will send back a response.

If the response is afirmative, the RPi will trigger an alarm and a LED reflector to scare the bear.

The server will publish essential info to a dashboard that could be accessed from a phone via MQTT apps.

HOW TO USE:
1. On your PI board you need to have: application_pi.py, camera_test.py, thermal_sensor_testing.py and relay_control.py
2. On your PC (or your MQTT server) you need to have the rest of the files
3. Turn on MQTT server and Flask server - application.py
4. Turn on MQTT client - application_pi.py
5. Check the webpage from Flask server to see the status
