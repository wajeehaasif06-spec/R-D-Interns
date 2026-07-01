import soundfile as sf

# Read the WAV file
audio_data, sample_rate = sf.read("loud.wav")

# Print basic information
print("Sample Rate:", sample_rate)
print("Shape:", audio_data.shape)
print("Data Type:", audio_data.dtype)

# Check if the audio is mono or stereo
if len(audio_data.shape) == 1:
    print("Channels: Mono")
else:
    print("Channels:", audio_data.shape[1])

# Calculate duration
duration = len(audio_data) / sample_rate
print("Duration:", duration, "seconds")