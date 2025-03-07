import time
import os
from datetime import datetime
from dotenv import load_dotenv
from mistyPy.Robot import Robot

# Load environment variables
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

misty = Robot(MISTY_IP)

def record():

    # Video filename on Misty's storage
    misty_video_filename = "test"
    width = 3840
    height = 2160

    # Start recording (5 seconds)
    #misty.start_recording_video(misty_video_filename, 5)
    misty.start_recording_video(fileName=misty_video_filename, mute=False, duration=5, width=width, height=height)


    print("Recording video for 5 seconds...")
    time.sleep(5)

    # Stop recording
    misty.stop_recording_video()

def check_video_list():

    # Retrieve the list of recorded videos
    video_list_response = misty.get_video_recordings_list()


    if video_list_response.status_code == 200:
        video_list = video_list_response.json().get("result", [])
        
        if video_list:
            print("Videos stored on Misty:")
            for video in video_list:
                print("-", video)
        else:
            print("No videos found on Misty's storage.")
    else:
        print(f"Failed to retrieve video list: {video_list_response.text}")
        
def save_clear_videos_on_misty():   
    # Retrieve the list of recorded videos
    video_list_response = misty.get_video_recordings_list()

    if video_list_response.status_code == 200:
        video_list = video_list_response.json().get("result", [])
        
        if video_list:
            
            print("Videos stored on Misty:")
            
            for video in video_list:
                
                print("-", video)
                # Retrieve and save each video
                response = misty.get_video_recording(video, base64=False)

                if response.status_code == 200:
                    
                    local_video_filename = f"{video}.mp4"
                    
                    if os.path.exists(local_video_filename):
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        local_video_filename = f"{video}_{timestamp}.mp4"
                        
                    with open(local_video_filename, "wb") as video_file:
                        
                        video_file.write(response.content)
                        
                    print(f"Video saved as {local_video_filename}")
                    misty.delete_video_recording(video)
                    
                else:
                    
                    print(f"Failed to retrieve video {video}: {response.text}")
                    
        else:
            
            print("No videos found on Misty's storage.")
            
    else:
        
        print(f"Failed to retrieve video list: {video_list_response.text}")

if __name__ == "__main__":
    record()
    #check_video_list()
    save_clear_videos_on_misty()