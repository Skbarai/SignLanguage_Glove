import serial
import joblib
import pandas as pd
import dictate

PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
MODEL_FILE = '../models(joblib)/Gesture_Model.joblib'

model = joblib.load(MODEL_FILE)

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
ser.reset_input_buffer()
ser.reset_output_buffer()

print(f"Serial connected on {PORT}. Receiving data...\n")

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            continue

        # DEBUG (remove later)
        # print("RAW:", line)

        if ',' not in line:
            continue

        parts = line.split(',')
        if len(parts) < 18:
            continue

        parts = parts[1:15]

        try:
            idxUp, idxLow, midUp, midLow, ringUp, ringLow, thumb, pinky, ax, ay, az, gx, gy, gz = map(float, parts)
        except ValueError:
            continue

        X_input = pd.DataFrame([[
            idxUp, idxLow, midUp, midLow,
            ringUp, ringLow, thumb, pinky,
            ax, ay, az, gx, gy, gz
        ]], columns=[
            'idxUp','idxLow','midUp','midLow',
            'ringUp','ringLow','thumb','pinky',
            'ax','ay','az','gx','gy','gz'
        ])

        pred = model.predict(X_input)[0]

        if pred == 0:
            label = 'ka'
            dictate.play_sound(dictate.CONSONANT_DIR + '/1.mp3')
        elif pred == 1:
            label = 'kha'
            dictate.play_sound(dictate.CONSONANT_DIR + '/2.mp3')
        elif pred == 2:
            label = 'ga'
            dictate.play_sound(dictate.CONSONANT_DIR + '/3.mp3')
        elif pred == 3:
            label = 'gha'
            dictate.play_sound(dictate.CONSONANT_DIR + '/4.mp3')
        elif pred == 4:
            label = 'nga'
            dictate.play_sound(dictate.CONSONANT_DIR + '/5.mp3')
        elif pred == 5:
            label = 'ek'
            dictate.play_sound(dictate.NUMBERS_DIR + '/1.mp3')
        elif pred == 6:
            label = 'dui'
            dictate.play_sound(dictate.NUMBERS_DIR + '/2.mp3')
        elif pred == 7:
            label = 'tin'
            dictate.play_sound(dictate.NUMBERS_DIR + '/3.mp3')
        elif pred == 8:
            label = 'char'
            dictate.play_sound(dictate.NUMBERS_DIR + '/4.mp3')
        else:
            label = 'unknown'

        print(f"Label: {label}")

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    ser.close()