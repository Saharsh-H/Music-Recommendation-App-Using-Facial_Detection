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

**Step 2:** Once the application opens, you'll see a GUI with a button labeled “Scan Mood & Recommend” and an input box for the number of songs you want recommended.

**Step 3:** Enter the number of songs you want (1–100), then click on the “Scan Mood & Recommend” button. The webcam will open

**Step 4:** Press the s key to capture your image, or Esc to cancel. The app will analyze your facial expression using DeepFace to detect your current mood. Based on your mood, it will recommend songs from the dataset that match the detected emotion.

## Requirements
* Python, CustomTkinter, Deepface and OpenCv should be installed on your machine.
* To install CustomTkinter or OpenCv, in your terminal window type "pip install customtkinter", "pip install opencv-python" and so on for the other libraries.
 

## Libraries/ Datasets used
1. OpenCV — Webcam image capture
2. Deepface — Facial emotion detection
3. Spotify API — Dataset
4. CustomTkinter — GUI
5. [Kaggle Spotify Dataset](https://www.kaggle.com/datasets/jg7demon/spotify-dataset-1921-2020-600k-tracks-with-mood/data?utm_source=chatgpt.com&select=MusicMoodFinal.csv)

## Group Members
**1. Saharsh S Hiremath:** Worked on 

**2. Vishudha Sood:** Worked on 

**3. Yash Sultania:** Worked on 
