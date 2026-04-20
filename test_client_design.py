import os
import requests

# --- Configuration ---
API_URL = "http://127.0.0.1:8880/v1/audio/speech/design"
OUTPUT_FOLDER = "./OUT_DESIGN"

# --- Voice Design Tasks ---
# Allowed parameter values:
# gender: male, female
# age: child, teenager, young adult, middle-aged, elderly
# pitch: very low pitch, low pitch, moderate pitch, high pitch, very high pitch
# style: whisper

TASKS = [
    {
        "id": "voice_male",
        "text": "Hello! This is an example of speech synthesis with an automatically generated male voice.",
        "gender": "male",
        "age": "middle-aged",
        "pitch": "moderate pitch",
        "style": ""
    },
    {
        "id": "voice_female",
        "text": "Hello! This is a middle-aged female voice with standard tone.",
        "gender": "female",
        "age": "middle-aged",
        "pitch": "moderate pitch",
        "style": ""
    },
    {
        "id": "voice_elderly",
        "text": "Good day. This is an elderly person's voice.",
        "gender": "male",
        "age": "elderly",
        "pitch": "low pitch",
        "style": ""
    },
    {
        "id": "voice_whisper",
        "text": "This is a whisper example. The voice is very quiet and calm.",
        "gender": "female",
        "age": "young adult",
        "pitch": "moderate pitch",
        "style": "whisper"
    },
    # Add your tasks below:
    # {
    #     "id": "my_custom_voice",
    #     "text": "Your text for synthesis here",
    #     "gender": "male",
    #     "age": "young adult",
    #     "pitch": "high pitch",
    #     "style": ""
    # },
]


def process_task(task, task_index):
    task_id = task.get("id", "voice")
    text = task.get("text", "")
    gender = task.get("gender", "")
    age = task.get("age", "")
    pitch = task.get("pitch", "")
    style = task.get("style", "")

    print(f"\n{'='*60}")
    print(f"🔹 Task #{task_index+1} | ID: {task_id}")
    print(f"📝 Text: {text[:70]}{'...' if len(text) > 70 else ''}")
    print(f"🎛️  Parameters: {gender} | {age} | {pitch} | {style}")

    if not text or not text.strip():
        print(f"⚠️  Skipped: empty text")
        return False

    try:
        data = {
            "text": text,
            "gender": gender,
            "age": age,
            "pitch": pitch,
            "style": style
        }

        print(f"➡️  Sending request to server...")
        response = requests.post(API_URL, data=data, timeout=120)

        if response.status_code == 200:
            # Generate filename: {id}_{gender}_{age}_{index}.wav
            gender_part = gender.lower().replace(" ", "_") if gender else "auto"
            age_part = age.lower().replace(" ", "_") if age else "auto"
            
            output_filename = f"{task_id}_{gender_part}_{age_part}_{task_index+1}.wav"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            # Save file
            with open(output_path, 'wb') as out:
                out.write(response.content)

            file_size = len(response.content)
            duration = round(file_size / (16000 * 2), 1)  # 16kHz 16bit mono

            print(f"✅ Success!")
            print(f"💾 Saved to: {output_path}")
            print(f"📊 Size: {file_size} bytes | Duration: {duration} sec")

            return True
        else:
            print(f"❌ Server error {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Processing error: {type(e).__name__}: {str(e)}")
        return False


def main():
    # Create folder if doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    total = len(TASKS)
    success = 0
    failed = 0

    print(f"🚀 Batch voice generation started")
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