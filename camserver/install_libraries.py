import subprocess

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def main():
    # Install p7zip-full
    run_command('sudo apt-get install -y p7zip-full')
    
    
    # GitClone
    
    run_command('sudo apt-get install git')
    run_command('cd /home') 
    run_command('git clone https://github.com/IcyG1045/CM4Cam.git)

    # Download and extract CM4_dt_blob.7z
    run_command('wget https://files.waveshare.com/upload/4/41/CM4_dt_blob.7z')
    run_command('7z x CM4_dt_blob.7z -O./CM4_dt_blob')

    # Change permissions and navigate into the directory
    run_command('sudo chmod 777 -R CM4_dt_blob')
    run_command('cd CM4_dt_blob')


    # Rename JSON files
    run_command('cd /usr/share/libcamera/ipa/rpi/vc4')
    run_command('sudo mv imx219.json imx219_ir.json')
    run_command('sudo mv imx219_noir.json imx219.json')

    # Install additional packages
    run_command('sudo apt install -y ffmpeg')
    run_command('sudo apt install -y python3 python3-pip')
    run_command('sudo apt install -y libcamera-tools')
    run_command('sudo apt-get install -y libopenblas-dev')

    # Install Python packages individually
    run_command('pip3 install picamera2')
    run_command('pip3 install Flask')
    run_command('pip3 install Flask-RESTful')
    run_command('pip3 install Pillow')
    run_command('pip3 install watchdog')
    run_command('pip3 install bcrypt')

    # Set permissions for specific directories
    run_command('sudo chmod u+rwx /home/cm4/cam/static/pictures/')
    run_command('sudo chmod u+rwx /home/cm4/cam/static/video/')
    run_command('sudo chmod -R 777 /home/cm4/cam/static/pictures/')
    run_command('sudo chmod -R 777 /home/cm4/cam/static/video/')

    # Reboot
    run_command('sudo reboot')

if __name__ == "__main__":
    main()
