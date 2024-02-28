import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import os
import glob

# Initialize GStreamer
Gst.init(None)

# Global variables to maintain the state of the camera and video writer
camera = None
video_writer = None

def get_next_video_number(filename):
    existing_files = glob.glob(f'{filename}_*.csv')
    max_number = 0
    for file in existing_files:
        # Extract the part of the filename that should contain the number
        file_number_part = file.replace('sensor_data_', '').replace('.csv', '')
        
        # Check if this part is a number
        if file_number_part.isdigit():
            number = int(file_number_part)
            max_number = max(max_number, number)

class CameraRecorder:
    def __init__(self):
        self.pipeline = None

    def start_camera_recording(self, filename):
        # Ensure the filename is in the local directory
        filename = f'{filename}_{get_next_video_number(filename)}'
        local_path = os.path.join(os.getcwd(), filename)

        # Define the GStreamer pipeline
        self.pipeline = Gst.parse_launch(f"""
            v4l2src ! video/x-raw, width=640, height=480, framerate=30/1 ! 
            videoconvert ! omxh264enc ! h264parse ! 
            mp4mux ! filesink location={local_path}
        """)
        
        # Set the pipeline to the PLAYING state
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop_camera_recording(self):
        if self.pipeline:
            # Send an EOS (End of Stream) signal to the pipeline
            self.pipeline.send_event(Gst.Event.new_eos())
            
            # Wait for the EOS to propagate through the pipeline
            self.pipeline.get_bus().timed_pop_filtered(
                Gst.CLOCK_TIME_NONE, Gst.MessageType.EOS
            )

            # Set the pipeline to the NULL state
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None

# Example usage
if __name__ == "__main__":
    recorder = CameraRecorder()
    recorder.start_camera_recording("output.mp4")
    # Recording for a certain duration or until a condition is met
    input("Press Enter to stop recording...")
    recorder.stop_camera_recording()