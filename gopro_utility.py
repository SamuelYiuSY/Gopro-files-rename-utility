import os
from collections import defaultdict
import shutil
import subprocess
from tqdm import tqdm

def create_output_directory(base_dir, folder_name="processed_videos"):
    """
    Create output directory for processed files.
    
    Args:
        base_dir (str): Base directory where to create the new folder
        folder_name (str): Name of the new folder
    
    Returns:
        str: Path to the created directory
    """
    output_dir = os.path.join(base_dir, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def group_gopro_files(input_directory="."):
    """
    Group GoPro video files by their video number and sort by part number.
    
    Args:
        input_directory (str): The directory containing the GoPro video files
    
    Returns:
        dict: Mapping of video numbers to their sorted original file paths
    """
    files = [f for f in os.listdir(input_directory) if f.endswith('.MP4') and f.startswith('GH')]
    video_groups = defaultdict(list)
    
    for filename in files:
        video_number = filename[4:8]
        video_groups[video_number].append(os.path.join(input_directory, filename))
    
    for video_number in video_groups:
        video_groups[video_number].sort(key=lambda x: x.split(os.path.sep)[-1][2:4])
    
    return video_groups

def get_video_duration(filepath):
    """Get duration of video file using ffprobe."""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            filepath
        ]
        output = subprocess.check_output(cmd).decode().strip()
        return float(output)
    except:
        return 0

def create_concat_file(video_paths, concat_file_path):
    """Create a concat demuxer file for ffmpeg."""
    with open(concat_file_path, 'w') as f:
        for video_path in video_paths:
            f.write(f"file '{os.path.abspath(video_path)}'\n")

def merge_videos_fast(video_paths, output_path, total_duration=None):
    """
    Merge videos using ffmpeg's concat demuxer without re-encoding.
    
    Args:
        video_paths (list): List of video file paths to merge
        output_path (str): Output path for merged video
        total_duration (float): Total duration of all videos for progress bar
    """
    try:
        # Create temporary concat file
        concat_file = output_path + '.txt'
        create_concat_file(video_paths, concat_file)
        
        # Prepare ffmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # Copy streams without re-encoding
            '-movflags', '+faststart',  # Enable fast start for web playback
            '-y',  # Overwrite output file if it exists
            output_path
        ]
        
        # Run ffmpeg command with progress bar
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if total_duration:
            pbar = tqdm(total=100, desc=f"Merging {os.path.basename(output_path)}")
            last_progress = 0
            
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                    
                # Try to parse progress from ffmpeg output
                if "time=" in line:
                    time_str = line.split("time=")[1].split()[0]
                    hours, minutes, seconds = map(float, time_str.split(':'))
                    current_duration = hours * 3600 + minutes * 60 + seconds
                    progress = min(100, int((current_duration / total_duration) * 100))
                    
                    if progress > last_progress:
                        pbar.update(progress - last_progress)
                        last_progress = progress
            
            pbar.close()
        
        process.wait()
        
        # Clean up concat file
        os.remove(concat_file)
        
        if process.returncode == 0:
            print(f"Successfully merged videos into: {output_path}")
        else:
            print(f"Error merging videos: ffmpeg returned code {process.returncode}")
            
    except Exception as e:
        print(f"Error merging videos: {e}")

def process_gopro_videos(input_directory=".", merge_videos=False):
    """
    Main function to process GoPro videos - rename and optionally merge them.
    
    Args:
        input_directory (str): Directory containing the original GoPro files
        merge_videos (bool): Whether to merge video parts or not
    """
    output_directory = create_output_directory(input_directory)
    video_groups = group_gopro_files(input_directory)
    
    if merge_videos:
        print("\nProcessing videos...")
        for video_number, file_paths in video_groups.items():
            if len(file_paths) > 1:
                output_path = os.path.join(output_directory, f"{video_number}.MP4")
                
                # Calculate total duration for progress bar
                total_duration = sum(get_video_duration(path) for path in file_paths)
                
                print(f"\nMerging parts for video {video_number}...")
                merge_videos_fast(file_paths, output_path, total_duration)
            else:
                # If there's only one part, just copy it
                output_path = os.path.join(output_directory, f"{video_number}.MP4")
                shutil.copy2(file_paths[0], output_path)
                print(f"Copied single video: {os.path.basename(file_paths[0])} -> {video_number}.MP4")
    else:
        # Rename files without merging
        for video_number, group_files in video_groups.items():
            for part_number, old_path in enumerate(group_files, 1):
                old_filename = os.path.basename(old_path)
                new_filename = f"{video_number}_{part_number}.MP4"
                new_path = os.path.join(output_directory, new_filename)
                
                try:
                    shutil.copy2(old_path, new_path)
                    print(f"Copied and renamed: {old_filename} -> {new_filename}")
                except OSError as e:
                    print(f"Error processing {old_filename}: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process GoPro video files')
    parser.add_argument('--input', '-i', default=".",
                      help='Input directory containing GoPro files')
    parser.add_argument('--merge', '-m', action='store_true',
                      help='Merge video parts after renaming')
    
    args = parser.parse_args()
    
    print(f"Processing files in directory: {args.input}")
    process_gopro_videos(args.input, args.merge)
    print("Processing complete!")