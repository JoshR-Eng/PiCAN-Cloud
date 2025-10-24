# PiCAN-Cloud: A CAN-to-Cloud Gateway

This project implements a robust, event-driven CAN-to-Cloud gateway on a Raspberry Pi. 
It is designed to bridge real-time data from a physical CAN bus to a cloud-hosted application - such as a digital twin.

Uses an interrupt-based listener to handle asynchronous CAN messages. This ensures most recent message is handles, even if the application's processing loop and the CAN bus cycle are not synchronized.

## Key Features

* **Event-Driven CAN Handling:** [`can_handler.py`] Inherits `CAN_Listener` from `python-can` package. Avoids the real-time limitation of polling (FIFO queues, data staleness) and guarantees most recent data.
* **DBC-Based:** Utilizes the `cantools` library with a `.dbc` file (e.g. `PiCAN.dbc`) for robust, scalable, and maintainable encoding and decoding of CAN messages.
* **Modular Architecture:** The application is split into three clear modules:
    * `src/PiCAN/can_handler.py`: Manages all CAN bus communication.
    * `src/Cloud/cloudClient.py`: Manages all HTTPS-based cloud communication.
    * `src/DataHandling/log.py`: Handles local data logging to CSV files.
* **Configurable:** All key parameters (CAN channel, bitrate, cloud URLs, log paths) are managed in a central `config.yaml` file.

## Hardware Requirements

* Raspberry Pi 3B+ or newer
* [Waveshare 2-CH CAN HAT](https://www.waveshare.com/wiki/2-CH_CAN_HAT)

## Installation & Setup
1.  **Connecting to WIFI**\* \
   \**IF you're running a fresh install of Raspberry Pi OS minimal* \
    \
    Run the command:
    ```bash
    sudo raspi-config
    ```
      1.  Navigate to `1 System Options` and press Enter.
      2.  Navigate to `S1 Wireless LAN` and press Enter.
      3.  Enter your Wi-Fi network name (SSID).
      4.  Enter your Wi-Fi password.
      5.  Select `Finish` to exit `raspi-config`. Your Raspberry Pi should now automatically connect to the Wi-Fi network.

3.  **Clone the Repository**
    ```bash
    git clone https://github.com/joshr-eng/pican-cloud
    cd pican-cloud
    ```

4.  **Enable SPI & Configure CAN HAT - FOR Waveshare 2-CH HAT** \
    This is a critical step for the Waveshare HAT to be recognized. \
    More details found at the wiki: [Waveshare 2-CH CAN HAT Wiki](https://www.waveshare.com/wiki/2-CH_CAN_HAT)

    * Enable the SPI interface:
        ```bash
        sudo raspi-config
        ```
        Navigate to `Interfacing Options` -> `SPI` -> `Yes`, and then reboot.

    * Edit the boot configuration file to load the CAN drivers:
        ```bash
        sudo nano /boot/config.txt
        ```
        Add the following lines to the end of the file:
        ```
        dtparam=spi=on
        dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=23
        dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25
        ```
        *Note: The interrupt pins (23, 25) are the defaults. Verify these with your HAT's documentation.*

    * Reboot the Raspberry Pi for the changes to take effect:
        ```bash
        sudo reboot
        ```

5.  **Install Software Dependencies** \
    Recommended to use a Python virtual environment - Particularly if RPi is being used for multiple for projects

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
6.  **Create Environment File**
    The current application structure loads the secure cloud URL from a `.env` file to security. \
    Create this file in the main project directory:
    ```bash
    nano .env
    ```
    Add the following line to the file, replacing the URL with your own:
    ```
    CloudURL="[[Your Cloud URL]]"
    ```

## Configuration

All system settings are controlled by `config.yaml`. Before running, review this file to match your setup \
Variables marked * are critical to general use case

* **`cloud`**:
  - *`cloud_return_variables` predefines expected values from the cloud
  - *`send_cloud_variables` predefines variables being sent to the cloud
  - `warmup_period` can be used if you want to train model in the cloud with some data before returning an updated parameter

* **`can`**: 
  - \*`bitrate` defines the CAN Bus bitrate in Kbps
  - \*`dbc` defines the name of the dbc file - this file should also be in the project root directory
  - `rbat_initial`* Optional, explicite to my use case as it defines default value to refer to

* **`rls`**:    
  - `covariance` Defines inital value of covariance for an RLS estimator in the cloud


## Usage

The `start.sh` script is intended to automatically initalisation venv, install dependencies and run `main.py`.

1.  Ensure you're in project directory:
    ```bash
    cd ~/PiCAN-Cloud
    ```
2.  Make the script executable:
    ```bash
    chmod +x start.sh
    ```

3.  Run the script:
    ```bash
    source start.sh
    ```
    This will activate the virtual environment, check dependencies and execute `main.py`.

## Code Overview
**'main.py`** is the main application entry point, entire code can be defined from this point \
#### General Structure
  1. **pkgs imports** - Imports all required packages and code modules
  2. **config import** - Imports all configuration and some variable initialisation
  3. **setup** - Defines `can`, `cloud` and `log` objects
  4. **loop** - main code function
    

#### Movement of Data
  1. CAN Listener waits until message is read on the CAN bus and holds most the most recent value
  2. `main.py` loop continously polls the CAN Buffer
  3. Variables are decrypted from CAN payload - it's bit strucutre, offset and scale defined by .dbc file
  4. CAN message is timestamped and `dt` is calculated from timestamp of previous data
  5. CAN payload & parameters defining estimators state are sent to the cloud
  6. If a valid response is received from the cloud, metrics are logged and updated parameter is returned to CAN bus


---
### **Deprecation Notice**

The files `src/PiCAN/can_bus.py` and `src/PiCAN/can_message.py` are obsolete. They represent an early, manual (polling-based) approach to CAN communication. The current implementation (`can_handler.py`) replaces those two and is event-driven, solving all asynchronous timing issues. These files are retained only as a reference.
