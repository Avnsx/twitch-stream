#!/usr/bin/python3
import subprocess, os, configparser, threading, time, sys, json
from datetime import datetime
from tkinter import filedialog, Tk
from time import sleep as s

class TwitchRecorder:
    def __init__(self, username, config_file='config.ini'):
        self.username = username
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.output_folder = None
        self.recording_process = None
        self.start_time = None
        self.output_filename = None
        self.is_recording = False
        self.stream_title = ""
        self.stream_category = ""
        
        self._setup_config()
        self._setup_output_folder()
    
    def _setup_config(self):
        print("🔧 Setting up configuration...")
        if not os.path.exists(self.config_file):
            self.config['DEFAULT'] = {'output_folder': ''}
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        self.config.read(self.config_file)
    
    def _setup_output_folder(self):
        self.output_folder = self.config['DEFAULT']['output_folder']
        
        if not self.output_folder:
            print('📁 Select output folder...')
            s(2)
            root = Tk()
            root.withdraw()
            self.output_folder = filedialog.askdirectory(title="Select Output Folder")
            root.destroy()
            
            if not self.output_folder:
                print("❌ No folder selected. Exiting.")
                sys.exit(1)
            
            self.config['DEFAULT']['output_folder'] = self.output_folder
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        
        if not os.path.exists(self.output_folder):
            print(f"❌ Output folder doesn't exist: {self.output_folder}")
            sys.exit(1)
    
    def _sanitize_filename(self, text):
        """Remove or replace characters that are invalid in Windows filenames"""
        if not text:
            return ""
        
        # Characters not allowed in Windows filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '-')
        
        # Replace quotes and other problematic characters
        text = text.replace('"', '').replace("'", '').replace('`', '')
        
        # Remove multiple consecutive spaces/dashes and strip
        import re
        text = re.sub(r'[-\s]+', ' ', text).strip()
        text = text.replace(' ', '_')
        
        return text[:50]  # Limit length
    
    def _check_stream_live(self):
        print(f"🔍 Checking if {self.username} is live...")
        try:
            result = subprocess.run([
                'streamlink', '--json', f'https://www.twitch.tv/{self.username}'
            ], capture_output=True, text=True, timeout=20, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print("✅ Stream is available")
                try:
                    stream_data = json.loads(result.stdout)
                    raw_title = stream_data.get('metadata', {}).get('title', '')
                    raw_category = stream_data.get('metadata', {}).get('category', '')
                    
                    self.stream_title = self._sanitize_filename(raw_title)
                    self.stream_category = self._sanitize_filename(raw_category)
                    
                    print(f"📊 Title: {raw_title}")
                    print(f"🎮 Category: {raw_category}")
                    print(f"📝 Sanitized title: {self.stream_title}")
                    print(f"📝 Sanitized category: {self.stream_category}")
                except Exception as e:
                    print(f"⚠️ Could not parse stream metadata: {e}")
                return True
            else:
                print(f"❌ Stream check failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Stream check timed out")
            return False
        except Exception as e:
            print(f"❌ Stream check error: {e}")
            return False
    
    def _create_filename(self):
        timestamp = datetime.now().strftime("%d_%m_%y-%H_%M")
        
        # Build filename with stream info
        parts = [self.username, timestamp]
        if self.stream_category:
            parts.insert(1, self.stream_category)
        if self.stream_title:
            parts.insert(-1, self.stream_title)
        
        filename = f'{"_".join(parts)}.mp4'
        self.output_filename = os.path.join(self.output_folder, filename)
        
        # Double-check the final filename is valid
        if len(filename) > 200:  # Windows path limit consideration
            # Shorten if too long
            filename = f"{self.username}_{timestamp}.mp4"
            self.output_filename = os.path.join(self.output_folder, filename)
        
        print(f"📝 Output: {filename}")
        print(f"📂 Full path: {self.output_filename}")
    
    def _set_title(self, title):
        try:
            safe_title = title.replace(":", "").replace("|", "-")
            if os.name == 'nt':
                os.system(f'title "{safe_title}"')
        except:
            pass
    
    def _status_monitor(self):
        while self.is_recording:
            try:
                if self.output_filename and os.path.exists(self.output_filename):
                    size_mb = os.path.getsize(self.output_filename) / (1024 * 1024)
                    if self.start_time:
                        elapsed = datetime.now() - self.start_time
                        duration = str(elapsed).split('.')[0]
                        status = f"🔴 RECORDING {self.username} - {duration} - {size_mb:.1f}MB"
                        self._set_title(status)
                        print(f"\r📊 {status}", end="", flush=True)
                time.sleep(3)
            except:
                break
    
    def start_recording(self):
        print(f"🎬 Starting recording of {self.username}")
        
        if not self._check_stream_live():
            print("❌ Stream not available")
            return False
        
        self._create_filename()
        self.start_time = datetime.now()
        self.is_recording = True
        
        print(f"⏰ Started at: {self.start_time.strftime('%H:%M:%S')}")
        
        # Start status thread
        threading.Thread(target=self._status_monitor, daemon=True).start()
        
        # Start recording
        cmd = ['streamlink', f'https://www.twitch.tv/{self.username}', 'best', '--output', self.output_filename]
        
        try:
            print("📡 Recording...")
            self.recording_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # Monitor output for errors/warnings
            for line in self.recording_process.stdout:
                if not self.is_recording:
                    break
                line = line.strip()
                if 'error' in line.lower() or 'critical' in line.lower():
                    print(f"\n❌ {line}")
                elif 'warning' in line.lower():
                    print(f"\n⚠️ {line}")
                elif line:  # Print non-empty lines for debugging
                    print(f"\n📡 {line}")
            
            return_code = self.recording_process.wait()
            self.is_recording = False
            
            return self._handle_completion(return_code)
            
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped by user")
            self._stop_recording()
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self._stop_recording()
            return False
    
    def _stop_recording(self):
        self.is_recording = False
        if self.recording_process:
            try:
                self.recording_process.terminate()
                self.recording_process.wait(timeout=5)
            except:
                try:
                    self.recording_process.kill()
                except:
                    pass
    
    def _handle_completion(self, return_code):
        if os.path.exists(self.output_filename):
            size_mb = os.path.getsize(self.output_filename) / (1024 * 1024)
            duration = datetime.now() - self.start_time if self.start_time else None
            
            print(f"\n🏁 FINISHED")
            print(f"📊 Size: {size_mb:.1f}MB")
            if duration:
                print(f"📊 Duration: {str(duration).split('.')[0]}")
            print(f"📂 Saved to: {self.output_filename}")
            
            if return_code == 0:
                self._set_title(f"Complete - {self.username} - {size_mb:.1f}MB")
                return True
            else:
                print(f"⚠️ Process returned code: {return_code}")
        else:
            print(f"❌ Output file not found: {self.output_filename}")
        
        print(f"⚠️ Finished with issues")
        return False

if __name__ == '__main__':
    streamer_name = input('Streamer Username to record: ')
    recorder = TwitchRecorder(streamer_name)
    
    try:
        if recorder.start_recording():
            print("🎉 Success!")
        else:
            print("😞 Failed")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
