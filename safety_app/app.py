from flask import Flask, render_template, redirect, url_for
import threading
import cv2
import os
import pygame
import time
import pywhatkit as kit
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)

# Global variables
is_recording = False
drive = None

# Function to authenticate Google Drive
def authenticate_google_drive():
    global drive
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(r"C:\Users\Prana\OneDrive\Desktop\client_secret_337588366203-nvo69ip94kk9niit1eqatbcso46fe3ua.apps.googleusercontent.com.json")
    gauth.LocalWebserverAuth()  # Opens the browser for authentication
    drive = GoogleDrive(gauth)
    print("Google Drive authenticated.")

# Function to play an alarm sound
def play_alarm_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(-1)

# Function to get the current location
def get_current_location():
    return "https://maps.app.goo.gl/8ndskgeUwADDETXi8"

# Function to send a WhatsApp message
def send_whatsapp_message():
    phone_number = "+919148546554"  # Replace with the recipient's phone number
    message = "Help! This is an emergency message."
    location_link = get_current_location()
    message_with_location = f"{message} \nMy location: {location_link}"

    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min

    # Schedule message 2 minutes in the future
    if minute >= 58:
        hour = (hour + 1) % 24
        minute = (minute + 2) % 60
    else:
        minute += 2

    kit.sendwhatmsg(phone_number, message_with_location, hour, minute)
    print("WhatsApp message has been scheduled.")

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for help button
@app.route('/help')
def help_button():
    sound_file = r"C:\Users\Prana\Downloads\cyber-alarms-synthesized-116358.mp3"
    # Start playing alarm sound
    threading.Thread(target=play_alarm_sound, args=(sound_file,)).start()
    # Start sending WhatsApp message
    threading.Thread(target=send_whatsapp_message).start()
    return redirect(url_for('index'))

# Function to capture video from webcam
def capture_video():
    global is_recording

    cap = cv2.VideoCapture(0)
    output_path = r'C:\Users\Prana\OneDrive\Desktop\output.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

    if not out.isOpened():
        print("Error: Could not open the output file.")
        return

    is_recording = True
    while is_recording:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        out.write(frame)

    cap.release()
    out.release()
    print(f"Video saved to: {output_path}")

# Route to start video recording
@app.route('/start_video')
def start_video():
    global is_recording
    is_recording = True
    # Start video recording in a separate thread
    threading.Thread(target=capture_video).start()
    return redirect(url_for('index'))

# Route to stop video recording and upload it to Google Drive
@app.route('/stop_video')
def stop_video():
    global is_recording
    is_recording = False  # Stop recording
    authenticate_google_drive()  # Authenticate Google Drive
    upload_video_to_drive()  # Upload the video
    return redirect(url_for('index'))

# Function to upload video to Google Drive
def upload_video_to_drive():
    file_name = 'output.avi'
    file_path = r'C:\Users\Prana\OneDrive\Desktop\output.avi'

    # Check if the file exists on Google Drive
    file_list = drive.ListFile({'q': f"title='{file_name}' and trashed=false"}).GetList()

    if file_list:
        print(f"File '{file_name}' found. Deleting old file...")
        for file in file_list:
            file.Delete()

    # Upload new file
    file_drive = drive.CreateFile({'title': file_name})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()

    print(f"New file '{file_name}' uploaded to Google Drive.")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
