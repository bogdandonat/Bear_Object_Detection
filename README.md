# Bear_Object_Detection
YOLO model for detecting brown bears on a custom dataset, deployment on MQTT server and visual input from Raspberry Pi 5

IoT solution with ML detection against bear's attacks

The ML model will be running on a MQTT Server.

The RPi 5 will send the input to the server, if there is any bear, the server will send back a response.

If the response is afirmative, the RPi will trigger an alarm and a LED reflector to scare the bear.

The server will publish essential info to a dashboard that could be accessed from a phone via MQTT apps.
