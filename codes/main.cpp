#include <mbed.h>
#include <mpr121.h>

// Setup the Serial for communication with Raspberry Pi
Serial pi(USBTX, USBRX);

// Setup the i2c bus on appropriate pins
I2C i2c(p9, p10); // Adjust pins according to your setup

// Setup the Mpr121
Mpr121 mpr121(&i2c, Mpr121::ADD_VSS);

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

// Ultrasonic sensor pins
DigitalOut trigPin(p6);
InterruptIn echoPin(p7);
Timer echoTimer;

int distance_mm = 0;

// ISR for echo pin rising/falling edge
void echo_isr() {
    if (echoPin.read() == 1) { // Rising edge
        echoTimer.reset();
        echoTimer.start();
    } else { // Falling edge
        echoTimer.stop();
        distance_mm = echoTimer.read_us() / 5.8; // Distance in mm (speed of sound is ~343m/s)
    }
}

int main() {
    pi.baud(9600); // Set baud rate for serial communication

    // Ultrasonic sensor setup
    trigPin = 0;
    echoTimer.reset();
    echoPin.rise(&echo_isr);
    echoPin.fall(&echo_isr);

    while (1) {
        // Trigger ultrasonic sensor
        trigPin = 1;
        wait_us(10); // 10us trigger pulse
        trigPin = 0;

        int value = mpr121.read(0x00);
        value += mpr121.read(0x01) << 8;

        // Check for key presses and send the data over serial
        for (int i = 0; i < 12; i++) {
            if ((value >> i) & 0x01) {
                char buffer[5]; // Buffer to hold the key code string and distance flag
                char distanceFlag = distance_mm > 500 ? '0' : '1'; // Check distance
                sprintf(buffer, "%02d%c\n", i, distanceFlag); // Format key code as two digits with distance flag
                pi.puts(buffer); // Send key code to Raspberry Pi as a string
                led2 = !led2; // Toggle LED2 as an indicator
            }
        }

        wait(0.01); // Add a small delay to debounce and prevent flooding the serial port
    }
}
