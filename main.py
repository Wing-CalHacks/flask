#import the getAudioTranscript from openai/audio.py


from open_ai.audio import getAudioTranscript
from open_ai.user.iterate_user_profile import strengthen_profile

# get the audio transcript

audio = getAudioTranscript("data/Rosemount Ln.m4a")
print(strengthen_profile("", audio, ["Nike shoes", "Adidas shirt"]))