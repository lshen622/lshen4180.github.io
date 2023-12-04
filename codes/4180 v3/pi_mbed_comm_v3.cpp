#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>

int main(int argc, char **argv) {
    int fd;
    char buf[4]; // Buffer to hold three characters and null-termination
    int n;

    // Open the Port
    fd = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) {
        perror("open_port: Unable to open /dev/ttyACM0 - ");
        return -1;
    }

    // Configure port for non-blocking read and apply settings
    fcntl(fd, F_SETFL, 0);
    struct termios options; 
    tcgetattr(fd, &options);   
    cfsetspeed(&options, B9600);   
    options.c_cflag &= ~CSTOPB;
    options.c_cflag |= CLOCAL;
    options.c_cflag |= CREAD;
    cfmakeraw(&options);
    tcsetattr(fd, TCSANOW, &options);
    sleep(1);

    // Open files for writing
    FILE *keycodeFile = fopen("keycodes.txt", "w");
    FILE *distanceFlagFile = fopen("distanceFlag.txt", "w");
    if (keycodeFile == NULL || distanceFlagFile == NULL) {
        perror("Unable to open file - ");
        if (keycodeFile) fclose(keycodeFile);
        if (distanceFlagFile) fclose(distanceFlagFile);
        return -1;
    }

    // Main loop to continuously read data from mbed
    while (1) {
        n = read(fd, buf, 3); // Read three characters at a time
        if (n < 0) {
            perror("Read failed - ");
            break;
        } else if (n == 0) {
            printf("No data on port\n");
        } else {
            buf[3] = 0; // Null-terminate the string
            printf("Received: %s\n", buf); // Print to terminal

            fprintf(keycodeFile, "%c%c\n", buf[0], buf[1]); // Write keycode to keycodeFile
            fflush(keycodeFile); // Flush keycodeFile buffer

            fprintf(distanceFlagFile, "%c\n", buf[2]); // Write distance flag to distanceFlagFile
            fflush(distanceFlagFile); // Flush distanceFlagFile buffer

            // Wait for the newline character
            read(fd, buf, 1); 
            if (buf[0] != '\n') {
                printf("Error: Expected newline character\n");
            }
        }
        sleep(0.01); // Adjust as needed
    }

    // Clean up and close the files and port
    fclose(keycodeFile);
    fclose(distanceFlagFile);
    tcdrain(fd);
    close(fd);
    return 0;
}
