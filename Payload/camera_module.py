import subprocess
import os
import logging
import shutil

def record_video(base_filename, segment_duration, total_duration, use_hardware_encoder=False, min_free_space_gb=1):
    """
    Records video in segments for a total duration, checking for available disk space.

    Args:
    base_filename (str): Base path for the output video files. Segments will be numbered.
    segment_duration (int): Duration of each video segment in seconds.
    total_duration (int): Total duration of the recording in seconds.
    use_hardware_encoder (bool): If True, uses hardware H.264 encoder; otherwise, uses software encoder.
    min_free_space_gb (int): Minimum free disk space in GB required to continue recording.
    """
    logging.info("Starting video recording")
    
    # Define the encoder
    encoder = "libx264"  # Default to software encoder
    if use_hardware_encoder:
        # encoder = "h264_omx"  # For older Raspberry Pi models
        encoder = "h264_v4l2m2m"  # For newer Raspberry Pi models

    # Calculate number of video segments
    num_segments = total_duration // segment_duration

    # FFmpeg command template
    command_template = [
        "ffmpeg",
        "-loglevel", "error",  # Suppresses all but error messages
        "-f", "v4l2",
        "-i", "/dev/video0",
        "-vcodec", encoder,
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-t", str(segment_duration),
        "-f", "mp4"
    ]

    for segment in range(num_segments):
        if not check_storage(min_free_space_gb):
            logging.error("Recording stopped due to insufficient disk space.")
            break

        filename = f"{base_filename}_segment{segment}.mp4"
        command = command_template + [filename]
        logging.info(f"Starting recording segment: {filename}")
        subprocess.run(command)
        logging.info(f"Finished recording segment: {filename}")

def get_free_space_gb(folder):
    """
    Returns the free disk space in gigabytes for the given folder.
    """
    total, used, free = shutil.disk_usage(folder)
    free_gb = free / 2**30  # Convert from bytes to gigabytes
    logging.debug(f"Free space: {free_gb} GB")
    return free_gb

def check_storage(min_free_space_gb, folder="/"):
    """
    Check if the available storage is above the minimum threshold.
    """
    free_space_gb = get_free_space_gb(folder)
    if free_space_gb < min_free_space_gb:
        logging.warning(f"Low disk space: Only {free_space_gb} GB left, which is below the threshold of {min_free_space_gb} GB.")
        return False
    return True