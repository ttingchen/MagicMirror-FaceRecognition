# SMAI V1.01 - Face Recognition Module

# Modified by: Pratik & Eben
# This is a modified script from the open source face recognition repo:
#https://github.com/ageitgey/face_recognition
# Patch update to fix bugs

import face_recognition
import picamera
import numpy as np
import sys
import os
import time
import pickle
import socket
import json

HOST = "192.168.137.141" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read(), encoding="latin1")

# Load a sample picture and learn how to recognize it.
# print("Loading known face image(s)")
# rec_image = face_recognition.load_image_file("/home/pi/MagicMirror/modules/MMM-Face-Recognition-SMAI/public/face.png")
# rec_face_encoding = face_recognition.face_encodings(rec_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []

id_check = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    client, clientInfo = s.accept()
    print("server recv from: ", clientInfo)
    print("message: ", client.recv(1024) )

    try:
        while 1:
            print("Capturing image.")
            # Grab a single frame of video from the RPi camera as a numpy array
            camera.capture(output, format="rgb")

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(output)
            print("Found {} faces in image.".format(len(face_locations)))
            face_encodings = face_recognition.face_encodings(output, face_locations)
            names = []
            face_id = "NoOne"
            curtime = time.ctime(time.time())
            name = ""

            # loop over the facial embeddings
            for encoding in face_encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                    encoding, 0.5)
                name = "Unknown" #if face is not recognized, then print Unknown

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                    curtime = time.ctime(time.time())

                face_id=name
                print(curtime,name)
                

            if name != "":
                f = open("/home/pi/MagicMirror/modules/MMM-Face-Recognition-SMAI/sample.txt", "w")
                f.write(face_id)
                f.close()
                result = {
                    "timestamp": curtime, 
                    "name": name,
                }
                pidata = json.dumps(result)  
                client.sendall(bytes(pidata,encoding="utf-8")) 
                time.sleep(30)
    except: 
        print("Closing socket")
        client.close()
        s.close()    


# while True:
#     print("Capturing image.")
#     # Grab a single frame of video from the RPi camera as a numpy array
#     camera.capture(output, format="rgb")

#     # Find all the faces and face encodings in the current frame of video
#     face_locations = face_recognition.face_locations(output)
#     print("Found {} faces in image.".format(len(face_locations)))
#     face_encodings = face_recognition.face_encodings(output, face_locations)
#     names = []
#     face_id = "Guest"
#     curtime = time.ctime(time.time())
    

#     # # Loop over each face found in the frame to see if it's someone we know.
#     # for face_encoding in face_encodings:
#     #     # See if the face is a match for the known face(s)
#     #     match = face_recognition.compare_faces([rec_face_encoding], face_encoding)
#     #     name = "<Unknown Person>"
   
#     #     if id_check == 0:
#     #         for file in os.listdir("/home/pi/MagicMirror/modules/MMM-Face-Recognition-SMAI/public"):
#     #             if file.endswith("-id.png"):
#     #                 face_id = file.replace('-', ' ').split(' ')[0]
#     #                 #print(face_id)
#     #         id_check = 0
#     #         #print(face_id) -- print the name you saved as the MM picture


#     #     if match[0]:
#     #         name = face_id
        
            

#     #     print("Person Detected: {}!".format(face_id))
#     #     f = open("/home/pi/MagicMirror/modules/MMM-Face-Recognition-SMAI/sample.txt", "w")
#     #     f.write(name)
#     #     f.close()
#     #     #time taken before the user is logged off from the mirror
#     #     time.sleep(15)
    
#     # loop over the facial embeddings
#     for encoding in face_encodings:
#         # attempt to match each face in the input image to our known
#         # encodings
#         matches = face_recognition.compare_faces(data["encodings"],
#             encoding)
#         name = "Unknown" #if face is not recognized, then print Unknown

#         # check to see if we have found a match
#         if True in matches:
#             # find the indexes of all matched faces then initialize a
#             # dictionary to count the total number of times each face
#             # was matched
#             matchedIdxs = [i for (i, b) in enumerate(matches) if b]
#             counts = {}

#             # loop over the matched indexes and maintain a count for
#             # each recognized face face
#             for i in matchedIdxs:
#                 name = data["names"][i]
#                 counts[name] = counts.get(name, 0) + 1

#             # determine the recognized face with the largest number
#             # of votes (note: in the event of an unlikely tie Python
#             # will select first entry in the dictionary)
#             name = max(counts, key=counts.get)

#             curtime = time.ctime(time.time())

#             #If someone in your dataset is identified, print their name on the screen
#             if currentname != name:
#                 currentname = name
#                 print(currentname)

# 		# update the list of names
#         # names.append(name)
#         face_id=currentname
#         print(curtime,name)
#         time.sleep(15)
        
#     f = open("/home/pi/MagicMirror/modules/MMM-Face-Recognition-SMAI/sample.txt", "w")
#     f.write(face_id)
#     f.close()
