# Music Recommendation App
Discover songs that vibe with your feelings!
This application uses real-time facial emotion recognition to detect your mood and recommends music that matches it—because your playlist should feel what you feel.

## Features
- Real-time webcam capture for mood detection
- Emotion classification using DeepFace
- Smart mood-to-music mapping (Happy → Upbeat, Sad → Mellow, etc.)
- Song recommendations using a Spotify dataset
- Option to select the number of song suggestions (1–100)
- Clean, dark-themed GUI built with CustomTkinter
- In-app logging for emotion status, recommendations, and errors

## How to use the app
**Step 1:** Open the main.py file and click on the "Run" button if you are on VS code. If you are using terminal, navigate to the "Music-Recommendation-App-Using-Facial_Detection" directory and type "python main.py"

**Step 2:** Once the application opens, a GUI will appear with the title “Mood-Based Music Recommender”.You’ll see:
- An input box to set the number of songs you want recommended (1–100)
- A button labeled “Scan Mood & Recommend”
- A disabled “Save Recommendations” button (it becomes active after a scan)

**Step 3:** Enter how many songs you want, then click “Scan Mood & Recommend”.
Your webcam will activate with a live preview.

**Step 4:** Press s to capture your image, or press Esc to cancel the scan.

**Step 5:** If a mood is detected and matching songs are found, a list of recommended songs will appear in the app, showing:
Song title
Artist
URL (if available)

## Requirements
* Python, CustomTkinter, Deepface and OpenCv should be installed on your machine.
* To install CustomTkinter or OpenCv, in your terminal window type "pip install customtkinter", "pip install opencv-python" and so on for the other libraries.
 

## Libraries/ Datasets used
1. OpenCV — Webcam image capture
2. Deepface — Facial emotion detection
3. Spotify API — Dataset
4. CustomTkinter — GUI
5. Pandas
6. Tkinter
7. [Kaggle Spotify Dataset](https://www.kaggle.com/datasets/jg7demon/spotify-dataset-1921-2020-600k-tracks-with-mood/data?utm_source=chatgpt.com&select=MusicMoodFinal.csv)

## Group Members
**1. Saharsh S Hiremath:** 
- Developed the core GUI using customtkinter
- Found and curated the entire Spotify songs dataset used for mood-based recommendations
- Designed logic for handling and preprocessing the CSV dataset

**2. Vishudha Sood:** 
- Integrated DeepFace to analyze facial expressions and determine the user’s dominant emotion.
- Developed a precise mapping system that translates detected emotions into mood categories.
- Utilized OpenCV to integrate camera functionality for capturing the user’s face in real time.
- Combined the emotion analysis with a recommendation logic that suggests songs matching the identified mood.

**3. Yash Sultania:**
-  Managed the song recommendation system and CSV parsing
- Added the Save Recommendations feature
- Converted song metadata into clickable URLs using Spotify track links and added them to the CSV
- Handled error messages, user input validation, and output formatting within the app
