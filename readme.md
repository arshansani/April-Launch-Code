# Texas Eclipse Ballooning Project

This repository contains the codebase for the Texas Eclipse Ballooning Project conducted during the April 8th eclipse. The project was undertaken by a team of 6 UT Austin Aerospace Engineering majors as their senior design project, under the guidance of Adam Nokes.

## Team Members
- Arshan Saniei-Sani
- Aytahn Benavi
- Matthew Nattier
- Samuel Mack
- Jason Deng
- Jonathan Williams

## Repository Structure

The repository is organized into two main folders:

1. **Ground Station**: This folder contains all the code deployed on the ground station. It is responsible for receiving data using an RFD900x, logging the data in a .csv format, and displaying the data using a rudimentary GUI.

2. **Payload**: This folder contains all the code deployed on the balloon. It is responsible for reading data from various sensors (Raspberry Pi Sense Hat V2, Thermocouple, GPS, 6 Axis IMU, and camera), storing it locally, and transmitting the data to the ground station using the RFD900x.

## Last-Minute Addition & Possible Error

Please note that an RSSI feed was added last minute, which is reflected in the ground station software but not in the payload code. This is because the RSSI feed was written directly on the Raspberry Pi right before the flight. While this may cause errors, it is not expected to have a significant impact on the overall functionality and should be a simple fix.

## Acknowledgments

This program was written by Arshan Saniei-Sani with the assistance of AI tools.

## Disclaimer

Please be aware that this repository was written very quickly, and as a result, there may be inconsistencies and poor documentation. We apologize for any inconvenience this may cause.

## Future Improvements

- Increase logging frequency
- Increase heartbeat frequency
- Simplify message format
- Add support for calibrating time based on GPS at startup