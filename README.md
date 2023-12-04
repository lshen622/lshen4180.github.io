<h1 align="center">ECE4180 Final Project: Whack-A-Mole</h1>
<p align="center">by Liyuan Shen, Wensi Huang, Tianyi Chu</p>

## Introduction
Welcome to our innovative version of the classic Whack-A-Mole game, reimagined with modern technology. This game offers a unique twist by incorporating an ultrasonic sensor and an MPR121 touchpad to provide a more interactive and engaging experience. 

In this game, players use the touchpad to select their desired difficulty level and to whack the moles that appear on the screen. The ultrasonic sensor adds an extra layer of interactivity, allowing players to use hand gestures to hit the moles, making the game more dynamic and physically engaging.

Our Whack-A-Mole game is not only entertaining but also demonstrates the potential of integrating various sensors and inputs into traditional gaming formats. It serves as an excellent example of how technology can be used to enhance the gaming experience, making it more immersive and enjoyable for players of all ages.


## Demo
The following video shows how the game is played.

![Demo Image](link_to_image)
[Video Demonstration](link_to_video)

## Operation Diagram

<figure align="center">
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/flowchart.jpg" alt="mbed image" width="100%">
</figure>

## Hardware and Wiring

<figure align="center">
    <figcaption>mbed LPC1767</figcaption>
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/mbed.jpg" alt="mbed image" width="10%">
</figure>

<figure align="center">
    <figcaption>Raspberry Pi 3</figcaption>
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/pi.jpg" alt="Pi image" width="20%">
    
</figure>

<figure align="center">
    <figcaption>Ultrasonic Distance Sensor</figcaption>
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/sensor.jpg" alt="sensor image" width="20%">
    
</figure>

<figure align="center">
    <figcaption>MPR121 Touch Pad</figcaption>
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/touchpad.jpg" alt="touchpad image" width="20%">
    
</figure>

<figure align="center">
    <figcaption>Pins for the peripherals</figcaption>
    <img src="https://github.com/lshen622/lshen4180.github.io/blob/main/images/pin.PNG" alt="touchpad image" width="20%">
    
</figure>


## Software

The first part of of our code is to develop the mbed code that can read in the ultrasonic sensor and touchpad's output. For the touchpad, we will read its output and convert them into a 2 digit char. The ultrasonic sensor's output is read and calculated. Then, the distance is compared with a preset number to determine if a hit condition is fulfilled. If the hit condition is not triggered, a "0" flag will be appended to the touchpad's msg. Otherwise, "1" is appended. Lastly, the code will send this 3 digit msg to the Raspberry Pi 3. The code for the mbed is attached below.

```cpp
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
```

Then next code is used on the pi to receive the msg sent from the mbed. This code will also write the first two digit to a file called keycodes.txt and the last digit to distanceFlag.txt. The code is shown below.

```cpp

```

