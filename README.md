# Twitch Stream Recorder
This Python code is a simple Twitch stream recorder using the asyncio and streamlink libraries, which allows you to record the best available quality livestream of one or multiple Twitch streamers and save the recordings as mp4 files to your computer. The reason I made this is, because other existing libraries were either broken or made things too complicated bothering people to get their Twitch API tokens etc.

## Features
* Record Twitch streams in real-time as they are happening
* Save streams as mp4 files
* Easy setup and usage
* Record multiple Twitch streamers simultaneously
* Implement logging and error handling

## Setup
1. Install the necessary Python libraries [with pip](https://youtu.be/9z7gGUbAj5U?t=13) through cmd / terminal:
```bash
pip install asyncio streamlink
```

2. Install `ffmpeg` and make sure it's declared as a system environment variable:
  * Guide for Windows: https://www.wikihow.com/Install-FFmpeg-on-Windows
  * All other Operating systems: https://www.hostinger.com/tutorials/how-to-install-ffmpeg

3. Clone or download the Twitch stream recorder repository from GitHub & extract the files.

4. Locate the extracted files and click on `twitch-recorder.py`

## Usage
The first time you start up the program, it will ask you to declare:
 1. An output folder location where all future live streams should be saved inside.
 2. The Twitch live streamer's username(s) you want to record (comma-separated for multiple streamers).

Once the code is running, it will retrieve the best available stream URL for the entered Twitch username(s), and then use the ffmpeg command to record the stream to a file in the specified output folder. The file name will include the Twitch username and the date and time at which the recorder was started.
The code will run continuously until you stop it manually with a keyboard interrupt (Ctrl+C on Windows & Linux, or Command+C on macOS).

After you set the recordings output folder location, it will create a file named `config.ini` which will store the location permanently, so you only need to enter any streamers' usernames you want to record in the future instead.

## Disclaimer
Please note that recording and distributing Twitch streams without the permission of the content creator may violate Twitch's terms of service and could lead to legal consequences. Use this code responsibly and with respect for the creators whose content you are recording.
