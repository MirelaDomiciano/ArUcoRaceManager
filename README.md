# ArUcoRaceManager

ArUcoRaceManager is a Python-based racing management system that uses ArUco markers for competitor detection and tracking. It provides functionalities for starting, pausing, resuming, and ending racing events, as well as for registering competitors and recording lap times.

## Features

- Detection and tracking of racing competitors using ArUco markers
- Management of racing events, including starting, pausing, resuming, and ending races
- Registration of competitors with their respective details such as name, vehicle model, and number
- Recording and storing lap times for each competitor
- Generation of race reports in text and PDF formats

## Requirements
- Python 3.x
- OpenCV
- NumPy
- ReportLab (for PDF generation)

## Installation
1. Clone this repository:
    ```
    git clone https://github.com/your-username/racing-lap-timer.git
    ```
2. Navigate to the project directory:
    ```
    cd racing-lap-timer
    ```
3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage
1. Prepare the competitors' registration data in a CSV file named `Registrations.csv`. The file should have the following columns:
    - Competitor Name
    - Competitor Motorcycle Model
    - Competitor Motorcycle Number
    - Other relevant information

2. Run the program:
    ```
    python racing_lap_timer.py
    ```
3. Follow the on-screen instructions to interact with the program:
    - Click on the camera window to give it focus.
    - Press 'f' to finish the race.

## Configuration
- Adjust the minimum lap completion time by modifying the `time_min` variable in the code.
