import asyncio
import configparser
import logging
import os
import streamlink
import subprocess
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, Tk
from time import sleep as s

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config_file_path = 'config.ini'
config = configparser.ConfigParser()

# Check if the config file exists, if not create one
if not Path(config_file_path).exists():
    config['DEFAULT'] = {'output_folder': ''}
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

# Load the config file
config.read(config_file_path)
twitch_usernames = input('Enter Streamer Usernames to record (comma-separated): ').split(',')
output_folder = config['DEFAULT']['output_folder']

# If the output_folder variable is not set, ask the user for input and open file explorer
if not output_folder:
    print('\nPlease choose the folder location where all future recordings should be saved.')
    s(3)
    root = Tk()
    root.withdraw()
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    config['DEFAULT']['output_folder'] = output_folder
    root.destroy()

# Save the variables to the config file
with open(config_file_path, 'w') as configfile:
    config.write(configfile)

os.system(f"title Recording {', '.join(twitch_usernames)} @ {output_folder}")

async def get_best_stream_url(username):
    try:
        twitch_stream_url = f"https://www.twitch.tv/{username}"
        streams = streamlink.streams(twitch_stream_url)
        if 'best' in streams:
            best_stream = streams['best']
            m3u8_url = best_stream.url
            logging.info(f"Will record from best livestream .m3u8 URL: {m3u8_url}")
            return m3u8_url
        else:
            logging.error("No available streams found.")
    except Exception as e:
        logging.error(f"Error getting stream URL: {e}")

async def record_stream(username):
    m3u8_url = await get_best_stream_url(username)
    if m3u8_url:
        try:
            output_path = Path(output_folder) / f"{username}_{datetime.now().strftime('%d_%m_%y-%H_%M')}.mp4"
            ffmpeg_cmd = ['ffmpeg', '-i', m3u8_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', str(output_path)]
            process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
            await process.communicate()
        except Exception as e:
            logging.error(f"Error recording stream: {e}")

async def record_multiple_streams(usernames):
    tasks = [record_stream(username.strip()) for username in usernames]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(record_multiple_streams(twitch_usernames))
