import customtkinter as ctk
from tkinter import messagebox
import cv2
from deepface import DeepFace
import pandas as pd
import threading
import os
import ast # Added import for literal_eval

# --- Configuration ---
# Build path relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILENAME = 'Songs Dataset.csv'
CSV_PATH = os.path.join(BASE_DIR, CSV_FILENAME)
RECOMMEND_LIMIT = 5

# --- Load and Prepare Dataset ---
songs_df = None # Initialize as None
load_error_msg = None # Initialize as None
try:
    # Consider checking if file exists first for a clearer error message
    # if not os.path.exists(CSV_PATH):
    #     raise FileNotFoundError(f"Dataset file not found at {CSV_PATH}")
    songs_df = pd.read_csv(CSV_PATH)

    # --- !!! IMPORTANT: YOU NEED TO EDIT THIS LINE !!! ---
    # --- Replace 'mood' with the ACTUAL column name from your CSV file ---
    # --- For example, if your column is called 'Mood' or 'Emotion', use that ---
    mood_column_name = 'mood' # <-- CHANGE 'mood' HERE to match your CSV header
    # --- !!! IMPORTANT: END OF EDIT SECTION !!! ---

    if mood_column_name not in songs_df.columns:
         raise KeyError(f"Column '{mood_column_name}' not found in {CSV_FILENAME}. Please check the column name in the script and CSV.")

    songs_df['mood_norm'] = songs_df[mood_column_name].str.lower()
    # --- End of the critical part for the KeyError ---

    if songs_df.empty:
        raise ValueError("Dataset is empty.")

except FileNotFoundError as e:
    songs_df = None
    load_error_msg = f"Dataset file not found: {e}"
except KeyError as e: # Specifically catch KeyError
     songs_df = None
     load_error_msg = f"Dataset Load Error: {e}" # Use the specific KeyError message
except Exception as e: # Catch other potential pandas/loading errors
    songs_df = None
    load_error_msg = f"Failed to load or process dataset '{CSV_FILENAME}': {e}"


# --- Recommend Songs from CSV ---
def recommend_songs_by_mood_csv(mood, limit=RECOMMEND_LIMIT):
    if songs_df is None:
        print("Warning: songs_df is None, cannot recommend.") # Added print warning
        return []

    # Ensure 'mood_norm' column exists before proceeding
    if 'mood_norm' not in songs_df.columns:
        print("Warning: 'mood_norm' column not found in DataFrame, cannot recommend.")
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
    key = mood_map.get(mood.lower(), 'happy') # Default to 'happy' if mood unknown
    filtered = songs_df[songs_df['mood_norm'] == key]
    sorted_df = filtered.sort_values('popularity', ascending=False)
    top = sorted_df.head(limit)

    recommendations = []
    for _, row in top.iterrows():
        artist = 'Unknown' # Default artist
        try:
            # Ensure it's a string before attempting literal_eval
            if isinstance(row['artists'], str):
                 # Use safer ast.literal_eval instead of eval
                artists_list = ast.literal_eval(row['artists'])
            else:
                # Assume it's already a list-like object if not a string
                artists_list = row['artists']

            # Check if artists_list is a non-empty list after evaluation/assignment
            if isinstance(artists_list, list) and artists_list:
                artist = artists_list[0] # Get the first artist

        except (ValueError, SyntaxError, TypeError) as e: # Catch specific errors from literal_eval or list access
            # Log potential parsing issues, but don't stop the whole process
            print(f"Warning: Could not parse artists for song '{row.get('name', 'N/A')}': {e}")
            # Keep artist as 'Unknown'

        # Check if required columns exist before accessing
        title = row.get('name', 'Unknown Title')
        popularity = row.get('popularity', 0)

        recommendations.append({
            'title': title,
            'artist': artist,
            'popularity': popularity
        })
    return recommendations

# --- Capture Face Image ---
def capture_face_image(filename='captured_face.jpg'):
    # Consider using tempfile for unique names if needed
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Provide a more specific error message
        raise RuntimeError("Could not access the webcam. Check camera permissions and connections.")
    while True:
        ret, frame = cap.read()
        if not ret:
            # If reading fails, inform the user or log
            print("Warning: Failed to grab frame from webcam.")
            continue # Try again or break after several failures

        cv2.imshow("Mood Capture - press 's' to save", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.imwrite(filename, frame)
            print(f"Image saved as {filename}")
            break
        elif key == 27: # Allow closing with ESC key
             print("Capture cancelled by user.")
             cap.release()
             cv2.destroyAllWindows()
             return None # Indicate cancellation

    cap.release()
    cv2.destroyAllWindows()
    return filename

# --- Detect Mood ---
def detect_mood(image_path):
    if image_path is None: # Handle case where capture was cancelled
        return None
    try:
        # Use enforce_detection=False to attempt analysis even if face detection confidence is low
        # It might return an empty list if no face is found.
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)

        # **FIX**: Check if analysis is a list and has at least one result dictionary
        if isinstance(analysis, list) and len(analysis) > 0 and isinstance(analysis[0], dict):
             # Check if 'dominant_emotion' key exists in the first result
             if 'dominant_emotion' in analysis[0]:
                return analysis[0]['dominant_emotion']
             else:
                # Log or show error if the expected key is missing
                error_msg = "Mood detection ran, but 'dominant_emotion' key not found in results."
                print(f"Warning: {error_msg}")
                # Avoid showing too many message boxes from background thread if possible
                # messagebox.showwarning("Detection Warning", error_msg)
                return None # Indicate missing key issue
        else:
             # Handle cases where no face was detected or analysis format is unexpected
             warn_msg = "Could not detect a face or analyze emotion from the image."
             print(f"Warning: {warn_msg}")
             # Optionally show a warning to the user, but avoid blocking the flow too much
             # messagebox.showwarning("Detection Warning", warn_msg)
             return None # Indicate no face/emotion detected

    except Exception as e: # Catching general Exception might still be needed for unforeseen DeepFace issues
        error_msg = f"Mood detection failed: {e}"
        print(f"Error: {error_msg}")
        # Avoid showing message box from background thread directly if possible
        # Consider logging to GUI instead: schedule_log_update(f"ERROR: {error_msg}")
        # messagebox.showerror("Detection Error", error_msg)
        return None

# --- GUI Application ---
class MoodRecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mood-Based Music Recommender")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # If dataset load failed, alert user immediately
        if load_error_msg:
            messagebox.showerror("Dataset Load Error", load_error_msg)
            # Optionally disable features or exit if dataset is critical
            # self.quit()

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Adjust row weights for output box

        # Header
        header = ctk.CTkFrame(self, corner_radius=10)
        header.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="🎵 Mood-Based Music Recommender 🎵", font=(None, 20, "bold")).grid(row=0, column=0, pady=10)

        # Controls Frame
        control_frame = ctk.CTkFrame(self, corner_radius=10)
        control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)

        self.scan_btn = ctk.CTkButton(control_frame, text="Scan Mood & Recommend", command=self.start_scan)
        self.scan_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Disable button if dataset failed to load or is None
        if songs_df is None:
            self.scan_btn.configure(state="disabled", text="Dataset Error - Cannot Scan")

        # Output Frame
        output_frame = ctk.CTkFrame(self, corner_radius=10)
        output_frame.grid(row=2, column=0, padx=20, pady=(10,20), sticky="nsew")
        output_frame.grid_rowconfigure(1, weight=1) # Make textbox expand
        output_frame.grid_columnconfigure(0, weight=1) # Make textbox expand

        ctk.CTkLabel(output_frame, text="Status & Recommendations:", font=(None, 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
        self.output_box = ctk.CTkTextbox(output_frame, height=300) # Removed fixed width
        self.output_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.output_box.configure(state="disabled") # Start disabled

    def start_scan(self):
        # Disable button immediately
        self.scan_btn.configure(state="disabled")
        # Clear previous output and show status
        self.log("Starting scan...\nCapturing image... Press 's' in the camera window or ESC to cancel.", clear=True)

        # Define the background task function
        def background_task():
            # --- Define helper functions for main thread GUI updates ---
            def schedule_log_update(message):
                # Ensure log is called in main thread
                self.after(0, lambda msg=message: self.log(msg))

            def schedule_button_update(state):
                 # Ensure button update is called in main thread
                self.after(0, lambda s=state: self.scan_btn.configure(state=s))

            img_path = None # Initialize image path
            try:
                img_path = capture_face_image()
                if img_path is None: # Check if capture was cancelled
                    schedule_log_update("Image capture cancelled.")
                    return # Exit the task early

                schedule_log_update("Image captured. Detecting mood...")
                mood = detect_mood(img_path) # detect_mood now handles its own message boxes for errors/warnings

                if not mood:
                    schedule_log_update("Mood detection failed or no mood detected.")
                    # No need to raise ValueError if detect_mood handles feedback
                else:
                    schedule_log_update(f"Detected Mood: {mood}\n")
                    schedule_log_update("Finding recommendations...")
                    recs = recommend_songs_by_mood_csv(mood)

                    if not recs:
                        schedule_log_update("No matching songs found in the dataset.")
                    else:
                        schedule_log_update("Recommendations:\n" + "="*20)
                        for idx, song in enumerate(recs, 1):
                            log_msg = f"{idx}. {song['title']} by {song['artist']} (Popularity: {song['popularity']})"
                            schedule_log_update(log_msg) # Schedule log update for each song
                        schedule_log_update("="*20 + "\nScan complete.")

            except Exception as e:
                 # Catch any other unexpected errors during the flow
                 error_msg = f"An unexpected error occurred during scan: {e}"
                 print(f"Error in background_task: {error_msg}") # Log to console
                 # Schedule error message in the GUI log
                 schedule_log_update(f"ERROR: {error_msg}")
                 # Optionally show a generic error message box (scheduled)
                 # self.after(0, lambda: messagebox.showerror("Unexpected Error", error_msg))

            finally:
                # **FIX**: Schedule button re-enabling in the main thread
                # Only re-enable if dataset loading was successful initially
                final_state = "normal" if songs_df is not None else "disabled"
                schedule_button_update(final_state)

                # Clean up captured image file if it exists
                if img_path and os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                        print(f"Cleaned up {img_path}")
                    except OSError as e:
                        print(f"Error removing temporary image {img_path}: {e}")


        # Start the background task in a separate thread
        threading.Thread(target=background_task, daemon=True).start()

    # Updated Log function with option to clear
    def log(self, msg, clear=False):
        try:
            self.output_box.configure(state="normal")
            if clear:
                self.output_box.delete("1.0", ctk.END)
            self.output_box.insert(ctk.END, msg + "\n")
            self.output_box.see(ctk.END) # Scroll to the end
            self.output_box.configure(state="disabled")
        except Exception as e:
            print(f"Error updating log box: {e}") # Log errors if updating fails

if __name__ == '__main__':
    app = MoodRecommenderApp()
    # Only run the app if dataset loading didn't raise an *initial* critical error shown in messagebox
    # The load_error_msg check inside __init__ handles showing the error popup
    app.mainloop()