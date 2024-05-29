import string
import numpy as np
from midiutil import MIDIFile
from scipy.io.wavfile import write
import os
import mido
from pydub import AudioSegment

# Function to map text to notes
def text_to_notes(text, note_mapping):
    notes = []
    for char in text:
        if char in note_mapping:
            notes.append(note_mapping[char])
    return notes

# Function to create a MIDI file from notes
def create_midi(notes, filename, tempo=120, duration=0.5):
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Track 0")
    midi.addTempo(track, time, tempo)

    channel = 0
    volume = 100

    for note in notes:
        midi.addNote(track, channel, note, time, duration, volume)
        time += duration

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

# Function to generate a sine wave for a given frequency
def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    wave = np.int16(wave * 32767)
    return wave

# Function to convert MIDI to audio
def midi_to_audio(midi_filename, sample_rate=44100):
    mid = mido.MidiFile(midi_filename)
    audio = np.array([], dtype=np.int16)
    for msg in mid.play():
        if msg.type == 'note_on' and msg.velocity > 0:
            freq = 440 * (2 ** ((msg.note - 69) / 12))  # Convert MIDI note to frequency
            wave = generate_sine_wave(freq, msg.time, sample_rate)
            audio = np.concatenate((audio, wave))
    return audio, sample_rate

# Function to encode text to MIDI and audio
def encode_text(text):
    notes = text_to_notes(text, note_mapping)
    midi_filename = "output.mid"
    create_midi(notes, midi_filename)
    print(f"MIDI file saved as {midi_filename}")
    audio, sample_rate = midi_to_audio(midi_filename)
    audio_segment = AudioSegment(audio.tobytes(), frame_rate=sample_rate, sample_width=audio.dtype.itemsize, channels=1)
    audio_filename = "output.mp3"
    audio_segment.export(audio_filename, format="mp3")
    print(f"Audio file saved as {audio_filename}")
    return midi_filename, audio_filename

# Function to decode MIDI to text
def decode_midi(midi_filename):
    decoded_text = ""
    for msg in mido.MidiFile(midi_filename).play():
        if msg.type == 'note_on' and msg.velocity > 0:
            for char, note in note_mapping.items():
                if note == msg.note:
                    decoded_text += char
    return decoded_text

# Function to decode audio to text
def decode_audio(audio_filename):
    audio = AudioSegment.from_mp3(audio_filename)
    audio.export("temp.wav", format="wav")
    sample_rate, audio_data = read("temp.wav")
    midi_filename = "temp.mid"
    write(midi_filename, sample_rate, audio_data)
    decoded_text = decode_midi(midi_filename)
    os.remove("temp.wav")
    os.remove(midi_filename)
    return decoded_text

# Function to remove all generated files
def remove_files():
    for file in os.listdir():
        if file.endswith(".mid") or file.endswith(".mp3"):
            os.remove(file)
    print("All generated files removed.")

# Define note mapping (example: A-Z to C4-F4)
note_mapping = {}
note_mapping.update(dict.fromkeys(string.ascii_lowercase[:4], 60))  # Map a-d to C4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[4:8], 62))  # Map e-h to D4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[8:12], 64)) # Map i-l to E4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[12:16], 65)) # Map m-p to F4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[16:20], 67)) # Map q-t to G4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[20:24], 69)) # Map u-x to A4
note_mapping.update(dict.fromkeys(string.ascii_lowercase[24:], 71))   # Map y-z to B4

# Menu loop
while True:
    print("Menu:")
    print("1. Encode text to MIDI and MP3")
    print("2. Decode MIDI to text")
    print("3. Decode MP3 to text")
    print("4. Remove all generated files")
    print("5. Exit")
    choice = input("Enter your choice (1/2/3/4/5): ")

    if choice == '1':
        text = input("Enter the text to encode: ")
        encode_text(text)
    elif choice == '2':
        midi_filename = input("Enter the MIDI file to decode: ")
        decoded_text = decode_midi(midi_filename)
        print("Decoded text:", decoded_text)
    elif choice == '3':
        audio_filename = input("Enter the MP3 file to decode: ")
        decoded_text = decode_audio(audio_filename)
        print("Decoded text:", decoded_text)
    elif choice == '4':
        remove_files()
    elif choice == '5':
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please try again.")