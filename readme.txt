# Control Panel Application Readme

## Overview
This project consists of two main components: a control panel application (`controlpanel.py`) designed to run on a client device, and a server (`main.py`) hosted on a base station. The control panel application offers a graphical interface for users to remotely trigger predefined commands on the base station. This setup allows for flexible, remote management of tasks configured and executed on the base station.

## Project Structure

### Control Panel Application (Client Side)
- `controlpanel.py`: Implements the graphical user interface for the control panel.
  - Features:
    - Navigate through tabs.
    - Add and customize buttons.
    - Link button actions to commands on the base station.

### Server (Base Station)
- `main.py`: Manages the execution of commands triggered by the control panel.
  - Capabilities:
    - Receives command triggers from the control panel.
    - Executes configured commands based on received triggers.
    - Allows for the configuration and customization of commands to be triggered by the control panel.

## Installation Requirements

To run both components of this project, you'll need Python 3.8 or later, along with the following Python packages:
- kivy
- kivymd
- socket

Install these packages using the command:

```
pip install kivy kivymd socket
```

*Note: Use `pip3` on MacOS or Linux systems.*

## Usage Instructions

### Configuring the Base Station
1. Configure commands and actions within `main.py` as needed for your specific application.
2. Start the server by running `main.py` on the base station.

### Setting Up the Control Panel
1. On the client device, run `controlpanel.py` to launch the control panel application.
2. Use the application to add buttons and configure them to trigger commands on the base station. Ensure the base station's IP address and port are correctly configured in the control panel application to facilitate communication.

Ensure the base station is operational and its network settings are correctly configured to allow for seamless communication with the control panel application.

## Additional Notes

- This system is designed for extensibility, allowing for easy customization of commands and control panel buttons to fit a wide range of use cases.
- The application and server must only be used for ethical purposes. Ensure you have the necessary permissions before triggering any actions on the base station.
- For support, customization help, or to report issues, please contact the developer.

*Made with help from Jetbrains AI assistant, gpt4, a few years of experience, and a TON of patience