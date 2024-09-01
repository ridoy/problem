from flask import Flask, request, jsonify, render_template
from pydub import AudioSegment
import os
import io
import boto3
import uuid
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

verse_filenames = [
    "cash.mp3",
    "fab.mp3",
    "kenzob.mp3",
    "bigsean.mp3",
    "laybanks.mp3",
    "luhtyler.mp3",
    "anycia.mp3",
    "chowlee.mp3",
    "kaliii.mp3",
    "6lack.mp3",
    "flomilli.mp3",
    "ynjay.mp3",
    "flee.mp3",
    "donq.mp3",
    "rob49.mp3"
]
def load_sections():
    directory = "./verses"
    sections = []
    for filename in verse_filenames:
        section_path = os.path.join(directory, filename)
        if os.path.exists(section_path):
            sections.append(AudioSegment.from_mp3(section_path))
        else:
            print(f"Section not found: {section_path}")
    return sections

def stitch_sections(sections, order):
    # TODO make out dir if doesn't exist
    # TODO add intro.mp3
    ordered_sections = []
    for index in order:
        if 1 <= index <= len(sections):
            ordered_sections.append(sections[index - 1])
        else:
            # TODO this should never happen, just throw an error
            return None, f"Invalid section number: {index}"

    if not ordered_sections:
        # TODO same here. Error out
        return None, "No sections selected."

    combined = ordered_sections[0]
    for section in ordered_sections[1:]:
        combined += section
        print(f"Current combined length: {len(combined) / 1000} seconds")
    
    print(f"Final combined length: {len(combined) / 1000} seconds")

    unique_filename = str(uuid.uuid4()) + ".mp3"
    combined.export("./out/" + unique_filename, format="mp3", bitrate="320k")
    # TODO: should be uuid/problem feat (verses user selected).mp3
    url = upload_to_s3("./out/" + unique_filename, "problem-customized", unique_filename)
    print(url)
    return url, None


def upload_to_s3(file_name, bucket, object_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        return f"https://{bucket}.s3.amazonaws.com/{object_name}"
    except NoCredentialsError:
        print("Credentials not available.")
        return None


@app.route('/stitch', methods=['POST'])
def stitch():
    data = request.json
    order = data.get("order")

    sections = load_sections()
    if not sections:
        return jsonify({"error": "No sections were loaded."}), 400

    url, error = stitch_sections(sections, order)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"generated_url": url})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

