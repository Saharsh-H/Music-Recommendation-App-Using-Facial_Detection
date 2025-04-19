import customtkinter as ctk
from tkinter import messagebox
import cv2
from deepface import DeepFace
import pandas as pd
import threading
import os

# --- Configuration ---
# Build path relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILENAME = 'Songs Dataset.csv'
CSV_PATH = os.path.join(BASE_DIR, CSV_FILENAME)
RECOMMEND_LIMIT = 5

# --- Load and Prepare Dataset ---
try:
    songs_df = pd.read_csv(CSV_PATH)
    songs_df['mood_norm'] = songs_df['mood'].str.lower()
    if songs_df.empty:
        raise ValueError("Dataset is empty.")
except Exception as e:
    songs_df = None
    # Show error when GUI starts
    load_error_msg = f"Failed to load dataset '{CSV_FILENAME}': {e}"
else:
    load_error_msg = None

# --- Recommend Songs from CSV ---
def recommend_songs_by_mood_csv(mood, limit=RECOMMEND_LIMIT):
    if songs_df is None:
        return []

    mood_map = {
        'happy': 'happy',
        'sad': 'sad',
        'neutral': 'calm',
        'angry': 'energetic',
        'fear': 'energetic',
        'surprise': 'energetic',
        'disgust': 'energetic'
    }
    key = mood_map.get(mood.lower(), 'happy')
    filtered = songs_df[songs_df['mood_norm'] == key]
    sorted_df = filtered.sort_values('popularity', ascending=False)
    top = sorted_df.head(limit)

    recommendations = []
    for _, row in top.iterrows():
        try:
            artists = eval(row['artists']) if isinstance(row['artists'], str) else row['artists']
            artist = artists[0] if artists else 'Unknown'
        except:
            artist = 'Unknown'
        recommendations.append({
            'title': row['name'],
            'artist': artist,
            'popularity': row['popularity']
        })
    return recommendations

# --- Capture Face Image ---
def capture_face_image(filename='captured_face.jpg'):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not access the webcam.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("Mood Capture - press 's'", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return filename

# --- Detect Mood ---
def detect_mood(image_path):
    try:
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        return analysis[0]['dominant_emotion']
    except Exception as e:
        messagebox.showerror("Error", f"Mood detection failed: {e}")
        return None

# --- GUI Application ---
class MoodRecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mood-Based Music Recommender")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # If dataset load failed, alert user
        if load_error_msg:
            messagebox.showerror("Dataset Load Error", load_error_msg)

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, corner_radius=10)
        header.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="🎵 Mood-Based Music Recommender 🎵", font=(None, 20, "bold")).grid(row=0, column=0, pady=10)

        # Controls
        control = ctk.CTkFrame(self, corner_radius=10)
        control.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        control.grid_columnconfigure(0, weight=1)
        self.scan_btn = ctk.CTkButton(control, text="Scan Mood & Recommend", command=self.start_scan)
        self.scan_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        if songs_df is None:
            self.scan_btn.configure(state="disabled")

        # Output
        output = ctk.CTkFrame(self, corner_radius=10)
        output.grid(row=2, column=0, padx=20, pady=(10,20), sticky="nsew")
        output.grid_rowconfigure(1, weight=1)
        output.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(output, text="Recommendations:", font=(None, 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
        self.output_box = ctk.CTkTextbox(output, width=560, height=300)
        self.output_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.output_box.configure(state="disabled")

    def start_scan(self):
        self.scan_btn.configure(state="disabled")
        self.log("Capturing image... Press 's' in the camera window.")

        def flow():
            try:
                img = capture_face_image()
                mood = detect_mood(img)
                if not mood:
                    raise ValueError("No mood detected.")
                recs = recommend_songs_by_mood_csv(mood)

                self.log(f"Detected Mood: {mood}\n")
                if not recs:
                    self.log("No matching songs found in dataset.")
                else:
                    for idx, song in enumerate(recs, 1):
                        self.log(f"{idx}. {song['title']} by {song['artist']} (Popularity: {song['popularity']})")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.log(f"Error: {e}")
            finally:
                self.scan_btn.configure(state="normal")

        threading.Thread(target=flow, daemon=True).start()

    def log(self, msg):
        self.output_box.configure(state="normal")
        self.output_box.insert(ctk.END, msg + "\n")
        self.output_box.see(ctk.END)
        self.output_box.configure(state="disabled")

if __name__ == '__main__':
    app = MoodRecommenderApp()
    app.mainloop()