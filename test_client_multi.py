import os
import requests
import glob
from datetime import datetime

# --- Configuration ---
API_URL = "http://127.0.0.1:8880/v1/audio/speech/clone"
OUTPUT_FOLDER = "./OUT"
OUT_DESIGN_FOLDER = "./OUT_DESIGN"


def get_audio_file_path(audio_path):
    """
    Check if the specified audio file exists.
    If not, scan OUT_DESIGN folder for .wav files and return the first found.
    Returns None if no suitable file is found.
    """
    if os.path.exists(audio_path):
        return audio_path

    # Scan OUT_DESIGN for .wav files
    wav_files = glob.glob(os.path.join(OUT_DESIGN_FOLDER, "*.wav"))

    if wav_files:
        print(f"⚠️  File not found: {audio_path}")
        print(f"🔍 Using fallback from {OUT_DESIGN_FOLDER}: {wav_files[0]}")
        return wav_files[0]

    return None


# --- Tasks list ---
# Add any number of tasks here for batch processing
TASKS = [
    {
        "id": "voice01",
        "text": "Hello! This is the first test text for speech synthesis.",
        "ref_text": "",
        "audio_file_path": "./OUT_DESIGN/voice_male_male_middle-aged_1.wav"
    },
    {
        "id": "voice01",
        "text": "Second example text with the same voice.",
        "ref_text": "",
        "audio_file_path": "./OUT_DESIGN/voice_male_male_middle-aged_1.wav"
    },
    {
        "id": "voice02",
        "text": "[laughter] А не пошел бы ты нахрен, со своими замашками! [laughter] .",
        "ref_text": "",
        "audio_file_path": "./OUT_DESIGN/voice_female_female_middle-aged_2.wav"
    },
    # Add new tasks below:
    # {
    #     "id": "custom_voice",
    #     "text": "Your text here",
    #     "ref_text": "Optional reference transcript",
    #     "audio_file_path": "./path/to/your/audio.wav"
    # },
]


def process_task(task, task_index):
    task_id = task.get("id", "unknown")
    text = task.get("text", "")
    ref_text = task.get("ref_text", "")
    audio_path = task.get("audio_file_path", "")

    print(f"\n{'='*60}")
    print(f"🔹 Task #{task_index+1} | ID: {task_id}")
    print(f"📝 Text: {text[:70]}{'...' if len(text) > 70 else ''}")

    if not text or not text.strip():
        print(f"⚠️  Skipped: empty text")
        return False

    resolved_audio_path = get_audio_file_path(audio_path)

    if not resolved_audio_path:
        print(f"❌ Error: reference audio not found {audio_path} and no .wav files in {OUT_DESIGN_FOLDER}")
        return False

    try:
        data = {
            "text": text,
            "ref_text": ref_text
        }

        with open(resolved_audio_path, 'rb') as f:
            files = {"ref_audio": f}

            print(f"➡️  Sending request to server...")
            response = requests.post(API_URL, data=data, files=files, timeout=120)

        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_filename = f"{task_id}_{task_index+1}_{timestamp}.wav"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            # Save file
            with open(output_path, 'wb') as out:
                out.write(response.content)

            file_size = len(response.content)
            duration = round(file_size / (16000 * 2), 1)  # 16kHz 16bit mono

            print(f"✅ Success!")
            print(f"💾 Saved to: {output_path}")
            print(f"📊 Size: {file_size} bytes | Approx duration: {duration} sec")

            return True
        else:
            print(f"❌ Server error {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Processing error: {type(e).__name__}: {str(e)}")
        return False


def main():
    # Create OUT folder if doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    total = len(TASKS)
    success = 0
    failed = 0

    print(f"🚀 Batch processing started")
    print(f"📋 Total tasks: {total}")
    print(f"📂 Output folder: {OUTPUT_FOLDER}")

    for index, task in enumerate(TASKS):
        result = process_task(task, index)
        if result:
            success += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"✅ Processing complete!")
    print(f"📊 Summary: total {total} | success {success} | failed {failed}")
    print(f"📂 All files saved to folder: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
