import asyncio, streamlink, subprocess, os, configparser
from datetime import datetime
from tkinter import filedialog, Tk
from time import sleep as s


config_file_path = 'config.ini'
config = configparser.ConfigParser()

# Check if the config file exists, if not create one
if not os.path.exists(config_file_path):
    config['DEFAULT'] = {'twitch_username': '',
                         'output_folder': ''}
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

# Load the config file
config.read(config_file_path)
twitch_username = config['DEFAULT']['twitch_username']
output_folder = config['DEFAULT']['output_folder']

# If the output_folder variable is not set, ask the user for input and open file explorer
if not output_folder:
    print('Please choose the Folder location, in which all future recordings should be saved into.\nA explorer window should open up soon ...')
    s(3)
    root = Tk()
    root.withdraw()
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    config['DEFAULT']['output_folder'] = output_folder
    root.destroy()

# If the twitch_username variable is not set, ask the user for input
if not twitch_username:
    twitch_username = input('Streamer Username to record: ')
    config['DEFAULT']['twitch_username'] = twitch_username

# Save the variables to the config file
with open(config_file_path, 'w') as configfile:
    config.write(configfile)

os.system(f"title {twitch_username} @ {output_folder}")

async def get_best_stream_url(username):
    # Construct the Twitch stream URL using the username
    twitch_stream_url = f"https://www.twitch.tv/{username}"

    # Use streamlink to retrieve the available streams for the Twitch stream URL
    streams = streamlink.streams(twitch_stream_url)

    # Check if the 'best' stream is available and get its .m3u8 URL
    if 'best' in streams:
        best_stream = streams['best']
        m3u8_url = best_stream.url
        print(f"Will record from best livestream .m3u8 URL: {m3u8_url}")
        return m3u8_url
    else:
        print("No available streams found.")

async def record_stream(username):
    m3u8_url = await get_best_stream_url(username)
    if m3u8_url:
        # Run ffmpeg command
        ffmpeg_cmd = ['ffmpeg', '-i', m3u8_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', f'{output_folder}\\{twitch_username} {datetime.now().strftime("%d_%m_%y - %H_%M")}.mp4']
        process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
        await process.communicate()

if __name__ == '__main__':    
    asyncio.run(record_stream(twitch_username))
