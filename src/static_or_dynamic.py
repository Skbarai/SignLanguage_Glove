import serial
from collections import deque

# --- Configuration ---
PORT = '/dev/ttyUSB0'        # Change to your USB port, e.g. '/dev/ttyUSB0' on Linux
BAUD_RATE = 115200
BUFFER_SIZE = 20
GYRO_THRESHOLD = 20  # |delta| > 20 means dynamic

# Indices of gx, gy, gz in each CSV row (0-based)
GX_IDX = 14
GY_IDX = 15
GZ_IDX = 16

def parse_row(line):
    """Parse a comma-separated line and return list of floats."""
    try:
        return [float(x) for x in line.strip().split(',')]
    except ValueError:
        return None

def is_dynamic(buffer):
    """
    Compare gyro values of the oldest and newest entries in the buffer.
    Returns True if any axis changed by more than GYRO_THRESHOLD.
    """
    oldest = buffer[0]
    newest = buffer[-1]

    delta_gx = abs(newest[GX_IDX] - oldest[GX_IDX])
    delta_gy = abs(newest[GY_IDX] - oldest[GY_IDX])
    delta_gz = abs(newest[GZ_IDX] - oldest[GZ_IDX])

    return delta_gx > GYRO_THRESHOLD or delta_gy > GYRO_THRESHOLD or delta_gz > GYRO_THRESHOLD

def main():
    buffer = deque(maxlen=BUFFER_SIZE)  # Circular buffer of size 10

    print(f"Opening port {PORT} at {BAUD_RATE} baud...")
    print(f"Gyro threshold: ±{GYRO_THRESHOLD} | Buffer size: {BUFFER_SIZE}")
    print("-" * 40)

    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            raw_line = ser.readline().decode('utf-8', errors='ignore')
            if not raw_line.strip():
                continue

            row = parse_row(raw_line)
            if row is None or len(row) < 14:
                print(f"[SKIP] Malformed line: {raw_line.strip()}")
                continue

            buffer.append(row)

            # Only classify once we have a full buffer
            if len(buffer) == BUFFER_SIZE:
                gesture = "DYNAMIC" if is_dynamic(buffer) else "STATIC"
                gx_old, gy_old, gz_old = buffer[0][GX_IDX], buffer[0][GY_IDX], buffer[0][GZ_IDX]
                gx_new, gy_new, gz_new = buffer[-1][GX_IDX], buffer[-1][GY_IDX], buffer[-1][GZ_IDX]
                print(
                    f"[{gesture}]  "
                    f"ΔGx={gx_new - gx_old:+.0f}  "
                    f"ΔGy={gy_new - gy_old:+.0f}  "
                    f"ΔGz={gz_new - gz_old:+.0f}"
                )
            else:
                print(f"[BUFFERING] {len(buffer)}/{BUFFER_SIZE} samples collected...")

if __name__ == "__main__":
    main()

# import serial
# from collections import deque

# --- Configuration ---
# PORT = '/dev/ttyUSB0'           # Change to your port, e.g. '/dev/ttyUSB0' on Linux
# BAUD_RATE = 115200
# BUFFER_SIZE = 5
# ACCEL_THRESHOLD = 0.25  # |delta| > 0.45 across buffer = dynamic

# # Indices of ax, ay, az in each CSV row (0-based)
# AX_IDX = 8
# AY_IDX = 9
# AZ_IDX = 10

# def parse_row(line):
#     """Parse a comma-separated line and return list of floats."""
#     try:
#         return [float(x) for x in line.strip().split(',')]
#     except ValueError:
#         return None

# def is_dynamic(buffer):
#     """
#     Compare accel values of the oldest and newest entries in the buffer.
#     Returns True if any axis changed by more than ACCEL_THRESHOLD.
#     """
#     oldest = buffer[0]
#     newest = buffer[-1]

#     delta_ax = abs(newest[AX_IDX] - oldest[AX_IDX])
#     delta_ay = abs(newest[AY_IDX] - oldest[AY_IDX])
#     delta_az = abs(newest[AZ_IDX] - oldest[AZ_IDX])

#     return delta_ax > ACCEL_THRESHOLD or delta_ay > ACCEL_THRESHOLD or delta_az > ACCEL_THRESHOLD

# def main():
#     buffer = deque(maxlen=BUFFER_SIZE)

#     print(f"Opening port {PORT} at {BAUD_RATE} baud...")
#     print(f"Accel threshold: ±{ACCEL_THRESHOLD} | Buffer size: {BUFFER_SIZE}")
#     print("-" * 40)

#     with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
#         while True:
#             raw_line = ser.readline().decode('utf-8', errors='ignore')
#             if not raw_line.strip():
#                 continue

#             row = parse_row(raw_line)
#             if row is None or len(row) < 11:
#                 print(f"[SKIP] Malformed line: {raw_line.strip()}")
#                 continue

#             buffer.append(row)

#             if len(buffer) == BUFFER_SIZE:
#                 oldest, newest = buffer[0], buffer[-1]
#                 delta_ax = newest[AX_IDX] - oldest[AX_IDX]
#                 delta_ay = newest[AY_IDX] - oldest[AY_IDX]
#                 delta_az = newest[AZ_IDX] - oldest[AZ_IDX]

#                 gesture = "DYNAMIC" if is_dynamic(buffer) else "STATIC"
#                 print(
#                     f"[{gesture}]  "
#                     f"ΔAx={delta_ax:+.3f}  "
#                     f"ΔAy={delta_ay:+.3f}  "
#                     f"ΔAz={delta_az:+.3f}"
#                 )
#             else:
#                 print(f"[BUFFERING] {len(buffer)}/{BUFFER_SIZE} samples collected...")

# if __name__ == "__main__":
#     main()


