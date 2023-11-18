import os
import base64
import time
from elevenlabs import generate, stream, Voice, VoiceSettings, set_api_key
from openai import OpenAI

OPENAI_API_KEY = "sk-."
set_api_key = "eleven-labs-api"

client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image(image_path):
    """Encodes the image at the given path to base64."""
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                raise
            time.sleep(0.1)


# def play_audio(text):
#     """Generates and plays audio from text."""
#     audio_stream = generate(
#         text=text, model="eleven_turbo_v2", stream=True,
#         voice=Voice(
#             voice='Johny Silverhand',
#             settings=VoiceSettings(stability=0.47, similarity_boost=0.73, style=0.0, use_speaker_boost=True)
#         )
#     )

#     # Stream the audio directly without saving to a file
#     stream(audio_stream)

def play_audio_openai(text): #openai tts
    """Generates and plays audio from text using OpenAI's TTS."""
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text,
    )
    response.stream_to_file(os.path.join("narration", "output.mp3"))

def generate_new_line(base64_image):
    """Generates a new line for the chat script."""
    return [
        {"role": "user", "content": [{"type": "text", "text": "Describe this image"},
                                     {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}] }
    ]

def analyze_image(base64_image, script):
    """Analyzes the image and returns generated text."""
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are Johny Silverhand from cyberpunk 2077 game. Roast the human that you see in the picture.
                Make it snarky and funny with your own style. Don't repeat yourself. Make it short. If I do anything remotely interesting, make a big deal about it!
                """
            }
        ] + script + generate_new_line(base64_image),
        max_tokens=500
    )
    return response.choices[0].message.content


def main():
    script = []

    while True:
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")
        base64_image = encode_image(image_path)

        print("👀 Johnny is watching...")
        analysis = analyze_image(base64_image, script=script)

        print("🎙️ Johnny says:")
        print(analysis)

        #play_audio(analysis) #elevenlabs

        play_audio_openai(analysis) #openai

        script.append({"role": "assistant", "content": analysis})

        time.sleep(5)

if __name__ == "__main__":
    main()