# Car-Trailer Two-DOF Vibration Analyzer
**ME4131 – Mechanical Vibration | NIT Rourkela | Group 1 (Resonance Duo)**

## What this application does
- Displays the idealised car–trailer two-degree-of-freedom model.
- Lets the user change car mass, trailer mass, and hitch stiffness.
- Calculates the two natural frequencies (including the zero-frequency rigid-body mode).
- Displays unnormalised and mass-normalised mode shapes.
- Checks mass orthogonality.
- Simulates undamped free-vibration time response for user-defined initial displacements and velocities.
- Displays a time-response graph and a browser-based animated car–trailer simulation with Play, Pause, and timeline controls.

## Requirements
- Python 3.9 or later
- Internet connection when loading the NIT Rourkela logo from Wikimedia Commons

## Installation (Windows)
1. Extract the ZIP file.
2. Open the extracted folder.
3. In the folder address bar, type `cmd` and press Enter.
4. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Start the application:
   ```bash
   streamlit run app.py
   ```
7. Streamlit will open the application in your browser. If it does not, open the local URL printed in the terminal (usually `http://localhost:8501`).

## Default values
- Car mass M = 2000 kg
- Trailer mass m = 1000 kg
- Hitch stiffness k = 180 kN/m

For these values, the expected results are:
- omega_1 = 0 rad/s; f_1 = 0 Hz (rigid-body translation)
- omega_2 = 16.4317 rad/s
- f_2 = 2.6152 Hz
- Mode 1 = [1, 1]^T
- Mode 2 = [1, -2]^T

## Model assumptions
The car and trailer are rigid translating masses, the hitch is a massless linear spring, and damping, road resistance, and external forces are neglected. Both bodies are free to translate horizontally, so the stiffness matrix has one zero eigenvalue.

## NIT Rourkela logo
The app uses the NIT Rourkela colour logo hosted on Wikimedia Commons. The file page identifies NIT Rourkela as its source/author and lists a CC0 dedication:
https://commons.wikimedia.org/wiki/File:NIT_Rourkela_Colour_Logo_Official.png

If your lab computer has no internet connection, replace `LOGO_URL` in `app.py` with a local image path and place the logo image in this folder.
