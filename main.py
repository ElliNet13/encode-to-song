import mido
from mido import MidiFile, MidiTrack, Message

# Define a special note number to represent line breaks
LINE_BREAK_NOTE = 128

# Function to check if a string contains non-ASCII characters
def contains_non_ascii(text):
    return any(ord(char) > 127 for char in text)

# Function to encode ASCII text as a MIDI file
def text_to_midi(text, output_filename):
    if contains_non_ascii(text):
        raise TypeError("The input contains non-ASCII characters.")

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    for char in text:
        if ord(char) <= 127:  # Check if the character is within the ASCII range
            note_number = ord(char)
        else:
            note_number = LINE_BREAK_NOTE  # Use the special note for non-ASCII characters

        track.append(Message('note_on', note=note_number, velocity=64, time=0))
        track.append(Message('note_off', note=note_number, velocity=64, time=480))  # Adjust timing as needed

    mid.save(output_filename)

# Function to decode MIDI file with ASCII text
def midi_to_text(input_filename):
    mid = MidiFile(input_filename)
    decoded_text = ""

    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on':
                note_number = msg.note
                if note_number == LINE_BREAK_NOTE:
                    char = '^'  # Use a placeholder character for non-ASCII notes
                else:
                    char = chr(note_number)  # Convert MIDI note to ASCII character
                decoded_text += char

    return decoded_text

if __name__ == "__main__":
    choice = input("Choose an operation (encode or decode): ").lower()

    if choice == "encode":
        input_option = input("Choose input option (text or txt file): ").lower()
        if input_option == "text":
            input_text = input("Enter the text to encode: ")
        elif input_option == "txt file":
            txt_file = input("Enter the path to the TXT file: ")
            with open(txt_file, "r") as file:
                input_text = file.read()
        else:
            print("Invalid input option. Please choose 'text' or 'txt file'.")
            exit(1)

        output_filename = input("Enter the output MIDI filename: ")

        # Encode ASCII text as MIDI
        text_to_midi(input_text, output_filename)
        print(f"Text encoded to MIDI: {output_filename}")

    elif choice == "decode":
        input_filename = input("Enter the input MIDI filename: ")
        decoded_text = midi_to_text(input_filename)

        output_option = input("Choose output option (display or txt file): ").lower()
        if output_option == "display":
            print(f"MIDI decoded to text:\n{decoded_text}")
        elif output_option == "txt file":
            output_txt_filename = input("Enter the path to save the decoded text (TXT file): ")
            with open(output_txt_filename, "w") as file:
                file.write(decoded_text)
            print(f"Decoded text saved to: {output_txt_filename}")
        else:
            print("Invalid output option. Please choose 'display' or 'txt file'.")

    else:
        print("Invalid choice. Please choose 'encode' or 'decode'.")