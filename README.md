# Bear_Object_Detection
YOLO model for detecting brown bears on a custom dataset, deployment on MQTT server and visual input from Raspberry Pi 4, User could see the output on a webpage created with flask that is running on the same server as MQTT broker

SHORT DESCRIPTION:

IoT solution with ML detection against bear's attacks

The ML model will be running on a MQTT Server.

The RPi 4 will send the input to the server, if there is any bear, the server will send back a response.

If the response is afirmative, the RPi will trigger an alarm and a LED reflector to scare the bear.

Also for backup there is a thermal camera that will capture the max temperature, if the temperature is bigger than a threshold (variable between day and night), this will trigger the alarm and the LED.

The server will publish essential info to a dashboard that could be accessed from a phone via MQTT apps.

HOW TO USE:
1. On your PI board you need to have: application_pi.py, camera_test.py, thermal_sensor_testing.py, ads_1115.py and relay_control.py
2. On your PC (or your MQTT server) you need to have the rest of the files
3. Turn on MQTT server and Flask server - application.py
4. Turn on MQTT client - application_pi.py
5. Check the webpage from Flask server to see the status

   
The web app is built with Flask for backend and HTML/CSS/JS for frontend. On the frontend the user could see the current image, and other informations regarding the system.
![image](https://github.com/user-attachments/assets/969da452-9e99-47c9-b56e-555869e281bb)

The system arhitecture is explained in the following image:

![image](https://github.com/user-attachments/assets/437e2332-d4cf-4be8-b7ca-feadde7b3ab6)

The RPI 4 sends input to the server via MQTT protocol that publishes the info on the online dashboard. The input is represented by 2 cameras, one optical and one thermal camera. The RPI 4 is wired to a relay module that triggers the Siren and LED reflector to scare the bears. The whole system is powered by a 12V Lead Acid battery, and to measure the battery percentage an ADC module is used. Also on the server a ML model for bear detection will run and scan the input from the RPI. If there is a bear, a response is sent back to the RPI to trigger the peripherals.

The results regarding the ML are shown below. There is a gradual descending for loss, both at training and validation. The precision and recall are growing in time, that means less false positives are detected and there are more bears detected over time. The precision mean at IoU of 50% is over 0.9 and at IoU between 50-95% is over 0.6. That means the model does not overfit and is capable of generalizing in diferrent scenarios.

![image](https://github.com/user-attachments/assets/0e6f870e-55a4-4144-906c-90a40c9be589)

Finally, the whole system is presented in the images below:

![image](https://github.com/user-attachments/assets/b8571bf5-610a-48cf-b41e-4c413d234046)

![image](https://github.com/user-attachments/assets/30d64315-b448-4c0f-b2c0-3f9735f9aac6)




