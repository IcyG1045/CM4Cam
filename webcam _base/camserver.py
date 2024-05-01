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

from libcamera import Transform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__, template_folder='template', static_url_path='/static')
app.secret_key = 'your_very_secret_key'  # Change this to a random secret key
api = Api(app)

encoder = H264Encoder()
output = CircularOutput()

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

    def get_frame(self):
        self.camera.start()
        with self.streamOut.condition:
            self.streamOut.condition.wait()
            self.frame = self.streamOut.frame
        return self.frame

    def VideoSnap(self):
        print("Snap")
        timestamp = datetime.now()
        print(timestamp)
        self.still_config = self.camera.create_still_configuration()
        self.file_output = "/home/cm4/cam/static/pictures/snap_%s.jpg" % timestamp
        time.sleep(1)
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

class VideoFeed(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))  # Ensure this follows your app's login logic
        return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Timestamp

def show_time():

    ''' Show current date time in text format '''

    rightNow = datetime.now()

    print(rightNow)

    currentTime = rightNow.strftime("%d-%m-%Y")

    print("date and time =", currentTime)



    return currentTime



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




@app.route('/startRec.html')

def startRec():

    """Start Recording Pane"""

    print("Video Record")

    basename = show_time()

    directory = basename

    parent_dir = "/home/cm4/cam/static/video/"

    output.fileoutput = (parent_dir + "vid_%s.h264"  %directory)

    output.start()



    return render_template('startRec.html')



@app.route('/stopRec.html')

def stopRec():

    """Stop Recording Pane"""

    print("Video Stop")

    output.stop()



    return render_template('stopRec.html')



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

@app.route('/files')

def files():

    image_directory = '/home/cm4/cam/static/pictures/'

    video_directory = '/home/cm4/cam/static/video/'

    try:

        images = os.listdir(image_directory)

        videos = [file for file in os.listdir(video_directory) if file.endswith(('.mp4', '.mkv'))]  # Assuming video formats



        # Filtering out system files like .DS_Store which might be present in directories

        images = [img for img in images if img.endswith(('.jpg', '.jpeg', '.png'))]



        return render_template('files.html', images=images, videos=videos)

    except Exception as e:

        return str(e)  # For debugging purposes, show the exception in the browser

api.add_resource(VideoFeed, '/cam')


users = {'admin': 'password'}  # This is an example; use secure password handling in production

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


# Your existing Flask routes and API definitions...


def create_image_thumbnail(image_path, thumbnail_path, size=(128, 128)):

    try:

        with Image.open(image_path) as img:

            img.thumbnail(size)

            img.save(thumbnail_path)

            print(f"Thumbnail successfully created for {image_path}")

    except Exception as e:

        print(f"Error creating thumbnail for {image_path}: {e}")


class ThumbnailHandler(FileSystemEventHandler):

    def on_created(self, event):

        if not event.is_directory and event.src_path.endswith(('.jpg', '.jpeg', '.png')):

            filename = os.path.basename(event.src_path)

            thumbnail_path = os.path.join(THUMBNAIL_DIRECTORY, filename)

            print(f"Detected new image: {event.src_path}")  # Debug print

            create_image_thumbnail(event.src_path, thumbnail_path)



IMAGE_DIRECTORY = '/home/cm4/cam/static/pictures'

THUMBNAIL_DIRECTORY = os.path.join(IMAGE_DIRECTORY, 'thumbnails')


def debug_directory_contents(directory):

    # Print out all files in the directory for debugging purposes

    print("Debugging directory contents:")

    for entry in os.scandir(directory):

        if entry.is_file():

            print(f"File: {entry.name}, Size: {entry.stat().st_size} bytes")



# Call this function in your api_files route or where you list the directory contents

debug_directory_contents(THUMBNAIL_DIRECTORY)


# Ensure the thumbnail directory exists

os.makedirs(THUMBNAIL_DIRECTORY, exist_ok=True)



# Optionally add video processing similar to image processing if needed

# Setup the watchdog observer

observer = Observer()

observer.schedule(ThumbnailHandler(), IMAGE_DIRECTORY, recursive=False)

observer.start()



# Ensure that the observer is stopped when the app exits

atexit.register(observer.stop)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
