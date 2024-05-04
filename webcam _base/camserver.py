##############################################################################################################################################################


                                                                        # Imports


##############################################################################################################################################################


import picamera2  # camera module for CM4-Nano-Cam
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import FileOutput, CircularOutput
import io

import subprocess
from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for
from flask_restful import Resource, Api, reqparse, abort
from PIL import Image
import atexit
from datetime import datetime
from threading import Condition
import time
import os
import numpy as np
import threading

from PIL import Image, ImageChops, ImageFilter
from libcamera import Transform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__, template_folder='template', static_url_path='/static')
app.secret_key = 'your_very_secret_key'  # Change this to a random secret key
api = Api(app)

encoder = H264Encoder()
output = CircularOutput()

import subprocess
import smtplib
from email.mime.text import MIMEText



##############################################################################################################################################################


                                                                        # Globals


##############################################################################################################################################################


# Global or session variable to hold the current recording file name
current_video_file = None

# GLobal set time for email time cooldown.
last_email_sent_time = 0

# Global Thread Lock
email_lock = threading.Lock()

# Global Last Motion Time
last_motion_time = None

# Global Email Routes
sender_email = "exapmle_sender@gmail.com"        # This has to be a gmail address
app_password = "Code You generated from google"  # The App Password you generated
receiver_email = "example_receiver@email.com"    # This can go to any email address

# Global Login Credentials CHANGE THEM
users = {'admin': 'password'}


##############################################################################################################################################################


                                                                        # H264 to MP4 Converter


##############################################################################################################################################################


def convert_h264_to_mp4(source_file_path, output_file_path):
    try:
        # Command to convert h264 to mp4
        command = ['ffmpeg', '-i', source_file_path, '-c', 'copy', output_file_path]
        subprocess.run(command, check=True)
        print(f"Conversion successful: {output_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
def show_time():
    """Return current time formatted for file names."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


##############################################################################################################################################################


                                                                        # Email Handler


##############################################################################################################################################################


def send_email(subject, body, sender, receiver, password):
    def email_thread():
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
    thread = threading.Thread(target=email_thread)
    thread.start()


##############################################################################################################################################################


                                                                        # Camera Handler


##############################################################################################################################################################


class Camera:
    def __init__(self):
        self.camera = picamera2.Picamera2()
        self.camera.configure(self.camera.create_video_configuration(main={"size": (800, 600)}))
        self.still_config = self.camera.create_still_configuration()
        self.encoder = MJPEGEncoder(10000000)
        self.streamOut = StreamingOutput()
        self.streamOut2 = FileOutput(self.streamOut)
        self.encoder.output = [self.streamOut2]
        self.camera.start_encoder(self.encoder)
        self.camera.start_recording(encoder, output)
        self.previous_image = None
        self.motion_detected = False  # Track if motion is currently detected
        self.email_allowed = True
        self.last_motion_detected_time = None  # Initialize to None
    def get_frame(self):
        self.camera.start()
        with self.streamOut.condition:
            self.streamOut.condition.wait()
            frame_data = self.streamOut.frame
        image = Image.open(io.BytesIO(frame_data)).convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.GaussianBlur(radius=2))  # Apply Gaussian blur
        if self.previous_image is not None:
            self.detect_motion(self.previous_image, image)
        self.previous_image = image
        return frame_data


##############################################################################################################################################################


                                                                        # Motion Detection Handler


    def detect_motion(self, prev_image, current_image):
        global last_motion_time
        current_time = time.time()
        diff = ImageChops.difference(prev_image, current_image)
        diff = diff.point(lambda x: x > 40 and 255)    #Adjust 40 to change sensitivity. Higher is less sensitve
        count = np.sum(np.array(diff) > 0)
        if count > 500:  # Sensitivity threshold for motion
            if self.email_allowed:
                # Motion is detected and email is allowed
                if last_motion_time is None or (current_time - last_motion_time > 30):
                    send_email("Motion Detected", "Motion has been detected by your camera.", sender_email, receiver_email, app_password)
                    print("Motion detected and email sent.")
                    last_motion_time = current_time  # Update the last motion time
                    self.email_allowed = False  # Prevent further emails until condition resets
                else:
                    print("Motion detected but not eligible for email due to cooldown.")
            else:
                print("Motion detected but email not sent due to recent activity.")
            self.last_motion_detected_time = current_time
        else:
            # No motion detected
            if self.last_motion_detected_time and (current_time - self.last_motion_detected_time > 30) and not self.email_allowed:
                self.email_allowed = True  # Re-enable sending emails after 30 seconds of no motion
                print("30 seconds of no motion passed, emails re-enabled.")
                self.last_motion_detected_time = current_time  # Reset to prevent message re-printing


##############################################################################################################################################################


                                                                        # Picture Snap Handler


##############################################################################################################################################################


    def VideoSnap(self):
        print("Snap")
        timestamp = datetime.now()
        print(timestamp)
        self.still_config = self.camera.create_still_configuration()
        self.file_output = f"/home/cm4/cam/static/pictures/snap_{timestamp}.jpg"
        self.job = self.camera.switch_mode_and_capture_file(self.still_config, self.file_output, wait=False)
        self.metadata = self.camera.wait(self.job)
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
camera = Camera()
def genFrames():
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


##############################################################################################################################################################


                                                                        # Login Redirector


##############################################################################################################################################################


class VideoFeed(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))  # Ensure this follows your app's login logic
        return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


##############################################################################################################################################################


                                                                        # @App Routes


##############################################################################################################################################################


@app.route('/startRec.html')
def startRec():
    """Start Recording Pane"""
    global current_video_file
    print("Video Record")
    basename = show_time()
    parent_dir = "/home/cm4/cam/static/video/"
    current_video_file = f"vid_{basename}.h264"  # Save the full path to a global variable
    output.fileoutput = os.path.join(parent_dir, current_video_file)
    output.start()
    return render_template('startRec.html')


@app.route('/stopRec.html')
def stopRec():
    """Stop Recording Pane"""
    global current_video_file
    print("Video Stop")
    output.stop()
    if current_video_file:
        source_path = os.path.join('/home/cm4/cam/static/video/', current_video_file)
        output_path = source_path.replace('.h264', '.mp4')
        convert_h264_to_mp4(source_path, output_path)
        return render_template('stopRec.html', message=f"Conversion successful for {output_path}")
    else:
        return render_template('stopRec.html', message="No video was recorded or file path is missing.")


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/home', methods = ['GET', 'POST'])
def home_func():
    """Video streaming home page."""
    return render_template("index.html")


@app.route('/info.html')
def info():
    """Info Pane"""
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('info.html')


@app.route('/srecord.html')
def srecord():
    """Sound Record Pane"""
    print("Recording Sound")
    timestamp = datetime.now()
    print(timestamp)
    subprocess.Popen('arecord -D dmic_sv -d 30 -f S32_LE /home/cm4/cam/static/sound/cam_$(date "+%b-%d-%y-%I").wav -c 2', shell=True)
    return render_template('srecord.html')


@app.route('/snap.html')
def snap():
    """Snap Pane"""
    print("Taking a photo")
    camera.VideoSnap()
    return render_template('snap.html')


@app.route('/api/files')
def api_files():
    image_directory = '/home/cm4/cam/static/pictures/'
    video_directory = '/home/cm4/cam/static/video/'
    try:
        images = [img for img in os.listdir(image_directory) if img.endswith(('.jpg', '.jpeg', '.png'))]
        videos = [file for file in os.listdir(video_directory) if file.endswith('.mp4')]
        print("Images found:", images)  # Debug print
        print("Videos found:", videos)  # Debug print
        return jsonify({'images': images, 'videos': videos})
    except Exception as e:
        print("Error in api_files:", str(e))  # Debug print
        return jsonify({'error': str(e)})


@app.route('/delete-file/<filename>', methods=['DELETE'])
def delete_file(filename):
    # Determine if it's a video or picture based on the extension or another method
    if filename.endswith('.mp4') or filename.endswith('.mkv'):
        directory = '/home/cm4/cam/static/video'
    else:
        directory = '/home/cm4/cam/static/pictures'
    file_path = os.path.join(directory, filename)
    try:
        os.remove(file_path)
        return '', 204  # Successful deletion
    except Exception as e:
        return str(e), 500  # Internal server error


@app.route('/files')
def files():
    image_directory = '/home/cm4/cam/static/pictures/'
    video_directory = '/home/cm4/cam/static/video/'
    try:
        images = os.listdir(image_directory)
        videos = [file for file in os.listdir(video_directory) if file.endswith(('.mp4'))]  # Assuming video formats
        # Filtering out system files like .DS_Store which might be present in directories
        images = [img for img in images if img.endswith(('.jpg', '.jpeg', '.png'))]
        return render_template('files.html', images=images, videos=videos)
    except Exception as e:
        return str(e)  # For debugging purposes, show the exception in the browser
api.add_resource(VideoFeed, '/cam')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))  # Redirect to index which will force login due to session check


@app.before_request
def require_login():
    allowed_routes = ['login', 'static']  # Make sure the streaming endpoints are either correctly authenticated or exempted here.
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect(url_for('login'))

##############################################################################################################################################################


                                                                        # Ip and Port Routing


##############################################################################################################################################################


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
