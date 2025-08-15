# fingerpy - Subway Surfers Controller

Control Subway Surfers on Poki using hand gestures detected via webcam!

## Features
- Uses OpenCV and MediaPipe for real-time pose detection.
- Controls the game in your browser using Selenium.
- Raise left/right/both hands or lower your head to move, jump, or slide.

## Setup

1. **Install Python 3.12** (required for MediaPipe).
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Download ChromeDriver** and place it in your PATH or project folder.  
   [Get ChromeDriver](https://chromedriver.chromium.org/downloads)

## Usage

```sh
python Subway-Surfers/Subway-Surfers.py
```

- Press `q` to quit.

## Requirements

See `requirements.txt`.

## Notes

- Make sure your webcam is connected.
- Only works with Python 3.12 or lower (MediaPipe limitation).
