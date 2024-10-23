from flask import Flask, request, jsonify, render_template
from pydub import AudioSegment
import os
import io
import boto3
import uuid
from botocore.exceptions import NoCredentialsError
import stat
from pathlib import Path
import subprocess

app = Flask(__name__)
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

acapella_paths = [
    "acapellas/cash.wav",
    "acapellas/kyle_rich.wav",
    "acapellas/kenzo_b.wav",
    "acapellas/lil_yachty.wav",
    "acapellas/lay_bankz.wav",
    "acapellas/big_sean.wav",
    "acapellas/fabolous.wav",
    "acapellas/anycia.wav",
    "acapellas/chow_lee.wav",
    "acapellas/6lack.wav"
]

def upload_to_s3(file_name, bucket, object_name):
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        return f"https://{bucket}.s3.amazonaws.com/{object_name}"
    except NoCredentialsError:
        print("Credentials not available.")
        return None


def get_beat_file(index):
    if index > 10 or index < 1:
        raise ValueError("Invalid beat index")
    return f"beats/full_beat_{index}.mp3"


def generate_ffmpeg_command(acapella_indices, acapella_paths, output_file_path):
    # TODO: ensure beat_index >= 1
    if any(idx >= len(acapella_paths) for idx in acapella_indices):
        raise ValueError("Invalid beat or acapella index")

    # Select the correct beat and acapella files
    beat_index = len(acapella_indices)
    beat_file = get_beat_file(beat_index)
    selected_acapellas = [acapella_paths[idx] for idx in acapella_indices]

    # Create the input arguments for FFmpeg
    input_args = f'-i {beat_file} ' + ' '.join([f'-i {acapella}' for acapella in selected_acapellas])

    # Create the filter complex argument
    filter_complex = []
    acapella_filters = []

    start_of_first_verse_ms = 10572.8
    eight_bars_ms = 24166.4
    # Set delays and volume adjustments for each acapella
    delays = [start_of_first_verse_ms + (eight_bars_ms * i) for i in range(len(acapella_indices))]  # Example delays; adjust as needed
    for i, acapella in enumerate(selected_acapellas):
        delay = delays[i]
        acapella_filter = f"[{i+1}]adelay={delay}|{delay}[a{i+1}]"
        acapella_filters.append(acapella_filter)

    # Construct the final filter complex
    filter_complex.extend(acapella_filters)
    mix_inputs = '[0]' + ''.join([f"[a{i+1}]" for i in range(len(selected_acapellas))])
    filter_complex.append(f"{mix_inputs}amix=inputs={len(selected_acapellas)+1}:duration=longest:normalize=0[mix]")

    # Combine the filter complex into a single argument
    filter_complex_str = '; '.join(filter_complex)

    # Construct the final FFmpeg command
    command = (
        f"ffmpeg {input_args} "
        f"-filter_complex \"{filter_complex_str}\" "
        f"-map \"[mix]\" -c:a libmp3lame -b:a 320k {output_file_path}"
    )

    return command


def run_command(command):
    """
    Execute the given command using subprocess.

    Parameters:
    - command (str): The command to execute.
    """
    try:
        # Execute the command
        process = subprocess.run(command, shell=True, check=True)
        if process.returncode == 0:
            print("Command executed successfully!")
        else:
            print("Command failed.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


@app.route('/stitch', methods=['POST'])
def stitch():
    data = request.json
    acapella_indices = data.get("order")

    unique_id = str(uuid.uuid4())
    output_file_path = f"out/{unique_id}.mp3"

    # TODO: handle error
    ffmpeg_command = generate_ffmpeg_command(acapella_indices, acapella_paths, output_file_path)
    # TODO: handle error
    run_command(ffmpeg_command)

    # TODO: handle error
    url = upload_to_s3(output_file_path, "problem-customized", "{}/problem.mp3".format(unique_id))

    # # TODO: formalize error response
    # if error:
    #     return jsonify({"error": error}), 400

    if url:
        return jsonify({"generated_url": url})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
