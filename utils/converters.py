import speech_recognition as sr
from io import BytesIO
from gtts import gTTS
import time
import subprocess
import os


def get_text(name):
    r = sr.Recognizer()
    with sr.AudioFile(f'{name}.wav') as source:
        audio = r.record(source)

    os.remove(f'{name}.ogg')
    os.remove(f'{name}.wav')
    return r.recognize_google(audio, language="ru-RU")


def convert_voice_to_text(audio_data: BytesIO) -> str:
    name = str(time.time())

    with open(f'{name}.ogg', 'wb') as new_file:
        new_file.write(audio_data.read())

    process = subprocess.run(['/usr/bin/ffmpeg', '-y', '-i', f'{name}.ogg', f'{name}.wav'])
    if process.returncode != 0:
        raise Exception("Something went wrong")

    return get_text(name)


def convert_text_to_voice(text):
    tts = gTTS(text=text, lang='ru')
    mp3 = BytesIO()
    tts.write_to_fp(mp3)
    return mp3.getvalue()
