from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pydub import AudioSegment
from gtts import gTTS
import tempfile
import uuid
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings, play, save


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def split_text_into_sentences(text):
    sentence_endings = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")
    sentences = sentence_endings.split(text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def change_audio_speed(audio, speed=1.0):
    return audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": int(audio.frame_rate * speed)},
        # change pitch
    ).set_frame_rate(audio.frame_rate)


def change_audio_pitch(audio, semitones=0):
    octaves = semitones / 12.0
    new_sample_rate = int(audio.frame_rate * (2.0**octaves))
    return audio._spawn(
        audio.raw_data, overrides={"frame_rate": new_sample_rate}
    ).set_frame_rate(audio.frame_rate)


@app.route("/convert", methods=["POST"])
def convert_text_to_audio():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug statement
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400

        sentences = split_text_into_sentences(text)
        if not sentences:
            return jsonify({"error": "No sentences found"}), 400

        # total_length = len(text)
        sentence_timings = []
        current_time = 0.0

        client = ElevenLabs(
            api_key="sk_9d7ed93ca9440bdcdd69c3ad7d01c9dd0ad9cb9bb4bba290",  # Defaults to ELEVEN_API_KEY
        )

        response = client.voices.get_all()

        unique_filename = f"{uuid.uuid4()}"
        wav_filepath = os.path.join(output_dir, f"{unique_filename}.wav")

        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_files = []
            for sentence in sentences:
                if not sentence:
                    continue
                try:
                    words = sentence.split()
                    more_space_text = "-".join(words)

                    print(more_space_text)
                    response = client.generate(
                        text=more_space_text,
                        voice=Voice(
                            voice_id="9RpXYdocFG8u7K3pqNxi",
                            settings=VoiceSettings(
                                stability=0.71,
                                similarity_boost=0.5,
                                style=0.0,
                                use_speaker_boost=True,
                            ),
                        ),
                    )
                    # tts = gTTS(sentence)
                    tts = response

                    print("Generated TTS for sentence:", tts)  # Debug statement
                    temp_file = os.path.join(tmpdirname, f"{uuid.uuid4()}.mp3")
                    # tts.save(temp_file)
                    save(response, temp_file)
                    temp_files.append(temp_file)
                except Exception as e:
                    print(f"Error generating TTS for sentence: '{sentence}'", e)
                    continue

            combined = AudioSegment.empty()
            for temp_file, sentence in zip(temp_files, sentences):
                segment = AudioSegment.from_file(temp_file)
                # segment = change_audio_speed(segment, speed=0.8)
                # segment = change_audio_pitch(segment, semitones=3)
                combined += segment
                duration = len(segment) / 1000.0
                sentence_timings.append(
                    {
                        "sentence": sentence.strip(),
                        "start_time": current_time,
                        "end_time": current_time + duration,
                    }
                )
                current_time += duration
            combined.export(wav_filepath, format="wav")

        return (
            jsonify(
                {
                    "message": "Text has been converted to audio successfully.",
                    "file_url": f"/download/{unique_filename}.wav",
                    "sentence_timings": sentence_timings,
                }
            ),
            200,
        )

    except Exception as e:
        print("Error:", e)  # Debug statement
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(output_dir, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
