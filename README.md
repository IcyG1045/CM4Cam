# A CM4-Nano-C based Flask security cam 

Streams, records video, and takes a picture with Picamera2 using a Raspi Compute Module 4 with a Waveshare CM4-Nano-C noir camera base board.



# To install and run, do the following

```
sudo apt-get install git
cd /home 
git clone https://github.com/IcyG1045/CM4Cam.git
```

Then,

```
cd /CM4Cam/camserver
sudo python3 install_libraries.py
```

It will install all required libraries as well as set correct permissions to run the CM4Cam. After completing, ### THE PI WILL REBOOT

Then do

```
sudo nano /boot/config.txt
```
add your required tags to enable your camera, then do

```
cd /home/CM4Cam/camserver
```
and run

```
sudo python3 camserver.py
```

This is based off of [allphasepi's work](https://github.com/allphasepi/Webcam/tree/main) which is based off [KarasuY's article](https://github.com/raspberrypi/picamera2/issues/844).



## You will need to set your credentials under the *Globals* section of camserver.py


```
sudo nano camserver.py
```

## This has only been tested on RaspberryPi OS legacy Bullseye 32bit using a 4gb wireless no-emmc Raspi Compute Module 4.


## 3d printed case link and creator [Metatron22](https://www.printables.com/@Metatron22_323085)

For the case, I had to cut off the bit that sticks out on the bottom half because it interfered with the wireless antennae. I also had to use screws to screw the two halves together because my pla print did not clip well.

[3d Printed Case](https://www.printables.com/en/model/358857-raspberry-pi-cm4-nano-base-c-case/files)


## Pictures

### 3d printed cased model


![cm4-nano-c 3d printed case](https://github.com/IcyG1045/CM4Cam/assets/80078028/2f286fb9-f90a-4288-b19e-964b7c149619)


### CM4-Nano-C with CM4
![cm4-nano-c](https://github.com/IcyG1045/CM4Cam/assets/80078028/87a9ac50-ae94-44de-bf3c-9b01b1564456)


### Mobile Phone View


![IMG_68999](https://github.com/IcyG1045/CM4Cam/assets/80078028/89bb749c-11e9-4bf1-8ef4-85c05fb28960)


### Desktop View
![Screenshot 2024-04-30 162934](https://github.com/IcyG1045/CM4Cam/assets/80078028/440f6ba5-4bdf-405a-9bc6-5574c16c0191)

