import serial
import json
import time
import os
import threading
from datetime import datetime
from pynput import keyboard

# ─────────────────────────────────────────────
# CONFIGURATION — edit these before running
# ─────────────────────────────────────────────
SERIAL_PORT   = "/dev/ttyUSB1"        
BAUD_RATE     = 115200
SAMPLE_INTERVAL_MS = 50       # milliseconds between samples
GESTURE_LABEL = "ka"       # change this per gesture
OUTPUT_FILE   = f"../JSON_DATA/{GESTURE_LABEL}.json"
# ─────────────────────────────────────────────

collecting   = False
should_exit  = False
samples      = []
session_count = 0

def parse_line(line: str, timestamp_ms: int) -> dict | None:
    """Parse a CSV line from Arduino into a structured sample dict."""
    try:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) != 14:
            return None

        (idxUp, idxLow, midUp, midLow,
         ringUp, ringLow, thumb, pinky,
         ax, ay, az, gx, gy, gz) = parts

        return {
            "timestamp": timestamp_ms,
            "flex": {
                "index_upper": float(idxUp),
                "index_lower": float(idxLow),
                "middle_upper": float(midUp),
                "middle_lower": float(midLow),
                "ring_upper":  float(ringUp),
                "ring_lower":  float(ringLow),
                "thumb":       float(thumb),
                "pinky":       float(pinky),
            },
            "accel": {
                "x": float(ax),
                "y": float(ay),
                "z": float(az),
            },
            "gyro": {
                "x": float(gx),
                "y": float(gy),
                "z": float(gz),
            }
        }
    except (ValueError, TypeError):
        return None


def load_existing(filepath: str) -> list:
    """Load existing gesture records from file, or return empty list."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_record(filepath: str, label: str, sample_list: list):
    """Append a new gesture record to the JSON file."""
    records = load_existing(filepath)
    records.append({
        "gesture_label": label,
        "sample_count": len(sample_list),
        "samples": sample_list
    })
    with open(filepath, "w") as f:
        json.dump(records, f, indent=2)


def on_press(key):
    global collecting, samples, session_count, should_exit

    if key == keyboard.Key.space:
        if not collecting:
            # ── START collecting ──
            samples = []
            collecting = True
            session_count += 1
            print(f"\n Recording started  (session #{session_count}) ..."
                  f"  Press SPACE to stop.")
        else:
            # ── STOP collecting ──
            collecting = False
            count = len(samples)
            if count > 0:
                save_record(OUTPUT_FILE, GESTURE_LABEL, samples)
                print(f"\n Stopped. {count} samples saved to '{OUTPUT_FILE}'")
            else:
                print("\n Stopped. No samples collected (nothing saved).")
            print("─" * 50)
            print("Press SPACE to record again, or Ctrl+C / ESC to exit.")

    elif key == keyboard.Key.esc:
        should_exit = True
        return False   # stop listener


def collection_loop(ser: serial.Serial):
    """Runs in background thread — reads serial and stores samples."""
    start_time = None

    while not should_exit:
        if collecting:
            if start_time is None:
                start_time = time.time()

            try:
                raw = ser.readline().decode("utf-8", errors="ignore")
                elapsed_ms = int((time.time() - start_time) * 1000)
                sample = parse_line(raw, elapsed_ms)
                if sample:
                    samples.append(sample)
            except serial.SerialException:
                print("\n Serial read error.")
                break

            # honour the sample interval
            time.sleep(SAMPLE_INTERVAL_MS / 1000.0)
        else:
            start_time = None   # reset for next session
            time.sleep(0.01)


def main():
    print("=" * 50)
    print(f"  Gesture Data Collector")
    print(f"  Label   : {GESTURE_LABEL}")
    print(f"  Port    : {SERIAL_PORT}  |  Baud: {BAUD_RATE}")
    print(f"  Output  : {OUTPUT_FILE}")
    print(f"  Interval: {SAMPLE_INTERVAL_MS} ms")
    print("=" * 50)

    # Check if file already has data
    existing = load_existing(OUTPUT_FILE)
    if existing:
        print(f"  ℹ  '{OUTPUT_FILE}' already has {len(existing)} record(s). New data will be appended.")
    print()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)   # let Arduino reset after connection
        ser.flushInput()
        print(f" Connected to {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f" Could not open serial port: {e}")
        return

    print("\nPress SPACE to start recording. ESC or Ctrl+C to exit.\n")
    print("─" * 50)

    # Serial reading runs in a background thread
    thread = threading.Thread(target=collection_loop, args=(ser,), daemon=True)
    thread.start()

    # Keyboard listener blocks until ESC or exception
    try:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except KeyboardInterrupt:
        pass

    print("\n Exiting.")
    ser.close()


if __name__ == "__main__":
    main()