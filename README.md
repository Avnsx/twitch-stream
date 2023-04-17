# Twitch Stream Recorder
This Python code is a simple Twitch stream recorder using the asyncio & streamlink libraries, which allows you to record the best available quality livestream of a Twitch streamer and save the recording as a mp4 file to your computer. The reason I made this is, because other existing libraries were either broken or made things too complicated bothering people to get their twitch API tokens etc.

## Features
* Record twitch streams right as they are happening
* Save streams as mp4
* Easy set up & usage

## Setup
1. Install the necessary python libraries [with pip](https://youtu.be/9z7gGUbAj5U?t=13) through cmd / terminal:
``pip install asyncio streamlink``

2. Install ``ffmpeg`` and make sure it's declared as a system environment variable
  
      Guide for Windows: https://www.wikihow.com/Install-FFmpeg-on-Windows
  
      All other Operating systems: https://www.hostinger.com/tutorials/how-to-install-ffmpeg

3. Clone or download the twitch stream recorder repository from GitHub & extract the files.

4. Locate the extracted files and click on ``twitch-recorder.py``

## Usage
The first time you start up the program, it will ask you to declare a;
 1. output folder location, where all future live streams should be saved inside.
 2. twitch live streamers username you want to record



Once the code is running, it will retrieve the best available stream URL for the entered Twitch username, and then use the ffmpeg command to record the stream to a file in the specified output folder. The file name will include the Twitch username and the date and time, which the recorder was started at.
The code will run continuously until you stop it manually with a keyboard interrupt (Ctrl+C on Windows & Linux, or Command+C on macOS).

After you set the recordings output folder location it will create a file named ``config.ini`` which will store the location permanently, so you only need to enter any streamers username you want to record in the future instead.

## Disclaimer
Please note that recording and distributing Twitch streams without the permission of the content creator may violate Twitch's terms of service and could lead to legal consequences. Use this code responsibly and with respect for the creators whose content you are recording.

