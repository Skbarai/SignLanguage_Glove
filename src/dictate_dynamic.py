import os

# Directories
CONSONANT_DIR = "../sounds/consonants_mp3"
WORD_DIR = "../sounds/words_mp3"
NUMBERS_DIR = "../sounds/numbers_mp3"

def play_sound(file_path):
        if os.path.exists(file_path):
            os.system(f"mpg123 '{file_path}' > /dev/null 2>&1")
        else:
            print(f"File not found: {file_path}")