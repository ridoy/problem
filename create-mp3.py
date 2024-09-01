from flask import Flask, request, jsonify, send_file
from pydub import AudioSegment
import os
import io

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

    return combined, None

@app.route('/stitch', methods=['POST'])
def stitch():
    data = request.json
    order = data.get("order")

    sections = load_sections(directory)
    if not sections:
        return jsonify({"error": "No sections were loaded."}), 400

    combined, error = stitch_sections(sections, order)
    if error:
        return jsonify({"error": error}), 400

    # Export to an in-memory file
    mp3_io = io.BytesIO()
    combined.export(mp3_io, format="mp3")
    mp3_io.seek(0)

    return send_file(mp3_io, mimetype="audio/mpeg", as_attachment=True, download_name="stitched_output.mp3")

if __name__ == "__main__":
    app.run(debug=True)
