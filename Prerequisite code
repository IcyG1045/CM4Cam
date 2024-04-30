Here is a list of prerequisit codes that must be enetered before running camserver.py

On the wavesahre website, https://github.com/IcyG1045/CM4Cam/tree/main
there is a a list of code needed to enable the camera.

sudo apt-get install p7zip-full
wget https://files.waveshare.com/upload/4/41/CM4_dt_blob.7z
7z x CM4_dt_blob.7z -O./CM4_dt_blob
sudo chmod 777 -R CM4_dt_blob
cd CM4_dt_blob/

After that, you need to add code to the config.txt under the boot folder. This is under the root directory under boot/config.txt

Use "cd .." until you get to the $ directory and the use 

sudo nano boot/config.txt

From there, scroll down to the bottom where it says [all] and add the following,

dtoverlay=imx219,cam0

press controll+x then press Y then press enter. 

sudo reboot

Upon rebooting Your camera should now work using

libcamerahello -t 0


The following code is necessary for the CM4-Nano-C waveshare base board because by default it uses the IRCAM tuning file when it should be using the NOIR tuning file. On the waveshare website, the path for where the tuning file is located is incorrect. The correct path is below.

cd usr/share/libcamera/ipa/rpi/vc4
sudo mv imx219.json imx219_ir.json
sudo mv imx219_noir.json imx219.json
