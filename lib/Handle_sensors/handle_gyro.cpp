#include "handle_gyro.h"
#include <Arduino.h>
#include <Wire.h>
#include "BluetoothSerial.h"

float values[10];
int16_t data[7];
float angleX = 0, angleY = 0, angleZ = 0;
unsigned long lastTime = 0;

float accXBuf[FILTER_SIZE] = {0};
float accYBuf[FILTER_SIZE] = {0};
float accZBuf[FILTER_SIZE] = {0};
float temperature[FILTER_SIZE] = {0};
float gyroX[FILTER_SIZE] = {0};
float gyroY[FILTER_SIZE] = {0};
float gyroZ[FILTER_SIZE] = {0};

void handle_gyro_init(int addr)
{
    Wire.begin();
    Wire.beginTransmission(addr);
    Wire.write(0x6B);
    Wire.write(0);
    Wire.endTransmission(true);
}

int16_t *Get_MPU_Data(int addr)
{
    
    Wire.beginTransmission(addr);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(addr, 14, 1);
    for (int i = 0; i < 7; i++)
    {
        // in sequence
        data[i] = Wire.read() << 8 | Wire.read(); // 0->acx, 1->acy, 2->acz,
                                                  // 3->Temp,
                                                  // 4->gyx, 5->gyy, 6->gyz
    }
    return data;
}
float *calc_values(int16_t *mpu_data)
{
    
    float AccX = mpu_data[0] / 16384.0;
    float AccY = mpu_data[1] / 16384.0;
    float AccZ = mpu_data[2] / 16384.0;
    float Temp = (mpu_data[3] / 340.0) + 36.53;
    float GyroX = mpu_data[4] / 131.0;
    float GyroY = mpu_data[5] / 131.0;
    float GyroZ = mpu_data[6] / 131.0;

    float GyroX_offset = 0.0; // e.g. 1.02
    float GyroY_offset = 0.0; // e.g. 0.98
    float GyroZ_offset = 0.0; // e.g. 0.05

    float GyroX_rate = GyroX;
    float GyroY_rate = GyroY;
    float GyroZ_rate = GyroZ;

    // GyroX_rate -= GyroX_offset;
    // GyroY_rate -= GyroY_offset;
    // GyroZ_rate -= GyroZ_offset;

   


    // Store readings in circular buffer
    accXBuf[bufIndex] = AccX;
    accYBuf[bufIndex] = AccY;
    accZBuf[bufIndex] = AccZ;
    temperature[bufIndex] = Temp;
    gyroX[bufIndex] = GyroX;
    gyroY[bufIndex] = GyroY;
    gyroZ[bufIndex] = GyroZ;

    bufIndex = (bufIndex + 1) % FILTER_SIZE;

    // Compute averages
    values[0] = 0; values[1] = 0; values[2] = 0; values[3] = 0; values[4] = 0; values[5] = 0; values[6] = 0;values[7] = 0; values[8] = 0; values[9] = 0;
    for (int i = 0; i < FILTER_SIZE; i++)
    {
        values[0] += accXBuf[i];
        values[1] += accYBuf[i];
        values[2] += accZBuf[i];
        values[3] += temperature[i];
        values[4] += gyroX[i];
        values[5] += gyroY[i];
        values[6] += gyroZ[i];
    }
    values[0] /= FILTER_SIZE;
    values[1] /= FILTER_SIZE;
    values[2] /= FILTER_SIZE;
    values[3] /= FILTER_SIZE;
    values[4] /= FILTER_SIZE;
    values[5] /= FILTER_SIZE;
    values[6] /= FILTER_SIZE;
     // --- Dead zone: ignore tiny drift when hand is static ---
    float DEAD_ZONE = 0.5; // °/s — tune this value
    if (abs(GyroX_rate) < DEAD_ZONE) GyroX_rate = 0;
    if (abs(GyroY_rate) < DEAD_ZONE) GyroY_rate = 0;
    if (abs(GyroZ_rate) < DEAD_ZONE) GyroZ_rate = 0;

    // --- Time delta ---
    unsigned long now = millis();
    float dt = (now - lastTime) / 1000.0; // seconds
    lastTime = now;

    // --- Integrate: angle += rate * dt ---
    angleX += GyroX_rate * dt;
    angleY += GyroY_rate * dt;
    angleZ += GyroZ_rate * dt;
    values[7] = angleX; // accumulated angle X (degrees)
    values[8] = angleY; // accumulated angle Y (degrees)
    values[9] = angleZ; // accumulated angle Z (degrees) 
 

    return values;
}
void Send_gyro_values(float *values_to_send)
{
    Serial.print(values_to_send[0], 2);
    Serial.print(",");
    Serial.print(values_to_send[1], 2);
    Serial.print(",");
    Serial.print(values_to_send[2], 2);
    Serial.print(",");
    Serial.print((values_to_send[4] < 0 && values_to_send[4] > -1) ? 0 : values_to_send[4], 0);
    Serial.print(",");
    Serial.print((values_to_send[5] < 0 && values_to_send[5] > -1) ? 0 : values_to_send[5], 0);
    Serial.print(",");
    Serial.print((values_to_send[6] < 0 && values_to_send[6] > -1) ? 0 : values_to_send[6], 0);
    Serial.print(",");
    Serial.print(values_to_send[7], 2);
    Serial.print(",");
    Serial.print(values_to_send[8], 2);
    Serial.print(",");
    Serial.print(values_to_send[9], 2);
    Serial.println();
}
