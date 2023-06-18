import os
import openai
openai.api_key = "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"
audio_file = open("data/K'NAAN - Wavin' Flag (Coca-Cola Celebration Mix).mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print (transcript)