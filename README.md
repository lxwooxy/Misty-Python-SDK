# Python SDK

Python library to work with your Misty robot. Currently in BETA. It is designed to follow a Pythonicated version of the naming convention within the [API Explorer](http://sdk.mistyrobotics.com/api-explorer/index.html).
There is a method generator built in to update the built in methods and available events, this works on all current Misty II product versions.

## Requirements

python >= 3.8

requests>=2.25.1<br>
websocket-client<=0.57.0<br>
yapf>=0.30.0
___
## Updating available commands and events
After installing the requirements, the first thing that should be done is updating the methods and events using the builtin generator.
```
# First import the RobotGenerator
from mistyPy.GenerateRobot import RobotGenerator

# Creating a new robot generator will rewrite the RobotCommands.py and Websocket.py 
# files to adjust them to the commands and websockets the robot has available
RobotGenerator("<IP_ADDRESS>")
```
___
## Running commands
To send commands to the robot first we need to initialize the connection to the robot.
```
# First import the robot object
from mistyPy.Robot import Robot

if __name__ == "__main__":
    ip_address = "<IP_ADDRESS>"
    # Create an instance of a robot
    misty = Robot(ip_address)
```

Sending the commands uses the REST API for Misty, so every return from a command will be a response object.
```
    current_response = misty.move_arms(30, 20)
    print(current_response)
    print(current_response.status_code)
    print(current_response.json())

    current_response = misty.get_log_level()
    print(current_response)
    print(current_response.status_code)
    print(current_response.json())
    print(current_response.json()["result"])
```
Output:
```
<Response [200]>
200
{'result': True, 'status': 'Success'}
<Response [200]>
200
{'result': {'local': 'Debug', 'remote': 'Debug'}, 'status': 'Success'}
{'local': 'Debug', 'remote': 'Debug'}
```
___
## Events
Subscribing to events is done through the Robot object. The list of available events are found in the Events class.
```
from mistyPy.Robot import Robot
from mistyPy.Events import Events
```

There are then two ways of interacting with the events. The first is to use a callback function for every new message returned after the successful subscription, the second is to reference the event object itself.
By default all event registrations are set to trigger once then unregister. To set an event registration to constantly trigger use the `keep_alive` parameter and set it to `True`.

Example: 

`misty.register_event(Events.VoiceRecord, "AudioCallbackEvent", callback_function=capture_speech_callback, keep_alive=True)`

### Using a callback function
```
# The callback function must only accept one parameter, which will be the event message data
def capture_speech_callback(data):
    print(data["message"])

if __name__ == "__main__":
    try:
        # First create the robot object
        ip_address = "<IP_ADDRESS>"
        misty = Robot(ip_address)

        # Register the event, which has a minimum of 2 parameters: the user defined name of the event, and the event type
        misty.register_event(Events.VoiceRecord, "AudioCallbackEvent", callback_function=capture_speech_callback)

        # Start recording speech to get an event message
        misty.capture_speech()

        # Use the keep_alive function to keep running the main python thread until all events are closed, or the script is killed due to an exception
        misty.keep_alive()

    except Exception as ex:
        print(ex)
    finally:
        # Unregister events if they aren't all unregistered due to an error
        misty.unregister_all_events()
```
Output:
```
{'errorCode': 0, 'errorMessage': 'Detected end of voice command.', 'filename': 'capture_Dialogue.wav', 'speechRecognitionResult': 'How are you doing?', 'success': True}
Event connection has closed for event: AudioCallbackEvent
```

### Using the Event object
```
if __name__ == "__main__":
    try:
        ip_address = "<IP_ADDRESS>"
        misty = Robot(ip_address)

        # Not including the callback_function parameter
        audio_callback_event = misty.register_event(Events.VoiceRecord, "AudioCallbackEvent")

        misty.capture_speech()

        # Wait for the event to get some data before printing the message
        while "just waiting for data" in str(audio_callback_event.data):
            pass

        print(audio_callback_event.data["message"])
    except Exception as ex:
        print(ex)
    finally:
        misty.unregister_all_events()

```
Output:
```
{'errorCode': 0, 'errorMessage': 'Detected end of voice command.', 'filename': 'capture_Dialogue.wav', 'speechRecognitionResult': 'What are you doing?', 'success': True}
```

## Adding event filters
There are built in methods for adding filters to the events. By default there are a handful of built in event specific filters. A sample are shown here:
```
from mistyPy.EventFilters import EventFilters

misty.register_event(Events.ActuatorPosition, "right_arm", condition=[EventFilters.ActuatorPosition.ArmRight])
```

The condition parameter takes a list of filters to apply, so the event conditions can be combined:
```
front_right = misty.register_event(Events.TimeOfFlight, "frontright",
    condition=[EventFilters.TimeOfFlightPosition.FrontRight, 
    EventFilters.TimeOfFlightDistance.MaxDistance(0.150),
    EventFilters.TimeOfFlightStatus.MaxStatus(102)])
```
There is also a method to build up your own filters that are not built in yet. The following example shows creating an event filter such that the returned voice record event must have an error code of 0 for the event to be triggered
```
misty.register_event(Events.VoiceRecord, "found_speech_result", condition=[EventFilters.event_filter("errorCode", "=", 0)])
```

# Notes

Section for my personal notes on the Python-SDK for Misty

On https://lessons.mistyrobotics.com/python/python-lessons/lesson-3-create-memories, Challenge 1, the first argument should be base64, not 65

On https://lessons.mistyrobotics.com/python-elements/misty-python-api/get-assets ```get_video_recording_list()``` should be ```get_video_recordings_list()``` instead

# Recording a 5 second video
```
misty.start_recording_video(fileName=misty_video_filename, mute=False, duration=5, width=1920, height=1080)
```

I've tried ```width = 3840``` and ```height = 2160``` which works, but swapping it results in the video not saving.

# Retrieve the list of recorded videos on Misty
```
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
```
# Retrieve and save the video

```
response = misty.get_video_recording(misty_video_filename, base64=False)

if response.status_code == 200:
    with open(local_video_filename, "wb") as video_file:
        video_file.write(response.content)
    print(f"Video saved as {local_video_filename}")
else:
    print(f"Failed to retrieve video: {response.text}")
```

