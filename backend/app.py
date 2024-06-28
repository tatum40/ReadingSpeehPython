from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pyttsx3
import os
from pydub import AudioSegment
import tempfile
import shutil
import uuid
import re

app = Flask(__name__)
CORS(app)

# Ensure the output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def split_text_into_sentences(text):
    # Split text based on the specified delimiters
    sentence_endings = re.compile(r"([.!?]|(?<=,))")
    sentences = sentence_endings.split(text)

    # Combine sentences and their delimiters
    combined_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        combined_sentences.append(sentences[i] + sentences[i + 1])

    # Add any remaining part of the text
    if len(sentences) % 2 != 0:
        combined_sentences.append(sentences[-1])

    return combined_sentences


@app.route("/tts", methods=["POST"])
def text_to_speech():
    try:
        text = request.json["text"]
        engine = pyttsx3.init()

        # Adjust the properties of the speech
        rate = engine.getProperty("rate")
        engine.setProperty("rate", rate - 50)

        volume = engine.getProperty("volume")
        engine.setProperty("volume", 0.9)

        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id)

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(output_dir, unique_filename)

        # Generate speech and save to the unique WAV file
        engine.save_to_file(text, filepath)
        engine.runAndWait()

        # Load the WAV file using pydub for duration calculation
        audio = AudioSegment.from_file(filepath, format="wav")

        # Split the text into sentences
        sentences = split_text_into_sentences(text)
        total_duration = len(audio) / 1000.0  # total duration in seconds

        # Calculate the duration of each sentence based on the proportion of text length
        sentence_lengths = [len(sentence) for sentence in sentences]
        total_text_length = sum(sentence_lengths)
        sentence_durations = [
            total_duration * (length / total_text_length) for length in sentence_lengths
        ]

        sentence_timings = []
        current_time = 0.0
        for sentence, duration in zip(sentences, sentence_durations):
            start_time = current_time
            end_time = current_time + duration
            sentence_timings.append(
                {
                    "sentence": sentence.strip(),
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )
            current_time = end_time

        return (
            jsonify(
                {
                    "message": "Text has been converted to speech and saved successfully.",
                    "file_url": f"/download/{unique_filename}",
                    "sentence_timings": sentence_timings,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(output_dir, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
