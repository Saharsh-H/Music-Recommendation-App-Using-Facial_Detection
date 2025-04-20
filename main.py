import customtkinter as ctk
from tkinter import messagebox, filedialog # Keep filedialog
import cv2
from deepface import DeepFace
import pandas as pd
import threading
import os
import ast
import webbrowser # Keep webbrowser if needed elsewhere, though not for clicking links here

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# --- Using the CSV with URLs ---
CSV_FILENAME = 'Songs_Dataset_with_URLs.csv'
CSV_PATH = os.path.join(BASE_DIR, CSV_FILENAME)

# --- Load and Prepare Dataset ---
songs_df = None
load_error_msg = None
try:
    if not os.path.exists(CSV_PATH):
         raise FileNotFoundError(f"Dataset file not found: {CSV_PATH}.")
    songs_df = pd.read_csv(CSV_PATH)
    mood_column_name = 'mood' # <-- CHANGE 'mood' HERE if needed
    if mood_column_name not in songs_df.columns:
         raise KeyError(f"Column '{mood_column_name}' not found in {CSV_FILENAME}.")
    songs_df['mood_norm'] = songs_df[mood_column_name].str.lower()
    if 'url' not in songs_df.columns:
        print(f"Warning: 'url' column not found in {CSV_FILENAME}.")
    if songs_df.empty: raise ValueError("Dataset is empty.")
except FileNotFoundError as e: songs_df = None; load_error_msg = f"Dataset file not found: {e}"
except KeyError as e: songs_df = None; load_error_msg = f"Dataset Load Error: {e}"
except Exception as e: songs_df = None; load_error_msg = f"Failed to load dataset: {e}"


# --- Recommend Songs from CSV ---
def recommend_songs_by_mood_csv(mood, limit=5):
    if songs_df is None: return []
    if 'mood_norm' not in songs_df.columns: return []
    mood_map = { 'happy': 'happy', 'sad': 'sad', 'neutral': 'calm', 'angry': 'energetic', 'fear': 'energetic', 'surprise': 'energetic', 'disgust': 'energetic' }
    key = mood_map.get(mood.lower(), 'happy')
    filtered = songs_df[songs_df['mood_norm'] == key]
    if 'popularity' not in filtered.columns: top = filtered.head(limit)
    else: sorted_df = filtered.sort_values('popularity', ascending=False); top = sorted_df.head(limit)
    recommendations = []
    for _, row in top.iterrows():
        artist = 'Unknown'
        try:
            artists_input = row.get('artists'); artists_list = []
            if isinstance(artists_input, str): artists_list = ast.literal_eval(artists_input)
            elif isinstance(artists_input, list): artists_list = artists_input
            if isinstance(artists_list, list) and artists_list: artist = artists_list[0]
        except (ValueError, SyntaxError, TypeError): pass
        title = row.get('name', 'Unknown Title'); popularity = row.get('popularity', 0); url = row.get('url', None)
        # Ensure URL is a string, replace NaN/None with empty string or placeholder
        url_str = str(url) if pd.notna(url) else "[No URL Found]"
        recommendations.append({ 'title': title, 'artist': artist, 'popularity': popularity, 'url': url_str })
    return recommendations

# --- Capture Face Image ---
def capture_face_image(filename='captured_face.jpg'):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): raise RuntimeError("Could not access webcam.")
    while True:
        ret, frame = cap.read();
        if not ret: continue
        cv2.imshow("Mood Capture - press 's' to save, ESC to cancel", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'): cv2.imwrite(filename, frame); print(f"Image saved: {filename}"); break
        elif key == 27: print("Capture cancelled."); cap.release(); cv2.destroyAllWindows(); return None
    cap.release(); cv2.destroyAllWindows(); return filename

# --- Detect Mood ---
def detect_mood(image_path):
    if image_path is None: return None
    try:
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
        if isinstance(analysis, list) and analysis and isinstance(analysis[0], dict): return analysis[0].get('dominant_emotion')
        print("Warning: Could not detect face/emotion."); return None
    except Exception as e: print(f"Error: Mood detection failed: {e}"); return None

# --- GUI Application ---
class MoodRecommenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mood-Based Music Recommender")
        self.geometry("600x650") # Height adjusted for save button
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")

        # --- Store current recommendations ---
        self.current_recommendations = []

        if load_error_msg: messagebox.showerror("Dataset Load Error", load_error_msg)

        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=0); self.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(self, corner_radius=10); header.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        header.grid_columnconfigure(0, weight=1); ctk.CTkLabel(header, text="🎵 Mood-Based Music Recommender 🎵", font=(None, 20, "bold")).grid(row=0, column=0, pady=10)
        control_frame = ctk.CTkFrame(self, corner_radius=10); control_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew") # Reduced pady
        control_frame.grid_columnconfigure(1, weight=1); ctk.CTkLabel(control_frame, text="Number of Songs (1-100):").grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.limit_entry = ctk.CTkEntry(control_frame, placeholder_text="e.g., 5", width=80); self.limit_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w"); self.limit_entry.insert(0, "5")
        self.scan_btn = ctk.CTkButton(control_frame, text="Scan Mood & Recommend", command=self.start_scan); self.scan_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=(5,5), sticky="ew")

        # --- ADDED: Save Button ---
        self.save_btn = ctk.CTkButton(control_frame, text="Save Recommendations", command=self.save_recommendations, state="disabled") # Start disabled
        self.save_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
        # --- End Save Button ---

        if songs_df is None: self.scan_btn.configure(state="disabled", text="Dataset Error")
        output_frame = ctk.CTkFrame(self, corner_radius=10); output_frame.grid(row=2, column=0, padx=20, pady=(10,20), sticky="nsew")
        output_frame.grid_rowconfigure(1, weight=1); output_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(output_frame, text="Status & Recommendations:", font=(None, 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
        self.output_box = ctk.CTkTextbox(output_frame); self.output_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- REMOVED Hyperlink Tag Configuration and Bindings ---
        # self.text_widget = self.output_box._textbox # No longer needed
        # self.text_widget.tag_configure(...) # Removed
        # self.text_widget.tag_bind(...) # Removed
        # self._links = {} # Removed
        # self.text_widget.bind("<KeyPress>", self._prevent_typing) # Removed

        # Just disable the box for editing
        self.output_box.configure(state="disabled")

    # --- REMOVED Hyperlink Event Handlers (_enter_link, _leave_link, _click_link, _prevent_typing) ---

    def get_validated_limit(self):
        default_limit = 5; max_limit = 100; min_limit = 1
        try: limit = int(self.limit_entry.get() or default_limit); return max(min_limit, min(limit, max_limit))
        except ValueError: self.log(f"Warning: Invalid limit. Using {default_limit}"); return default_limit
        except Exception as e: self.log(f"Error reading limit: {e}. Using {default_limit}"); return default_limit

    # --- ADDED: Method to Save Recommendations ---
    def save_recommendations(self):
        """Saves the current list of recommendations to a text file."""
        if not self.current_recommendations:
            messagebox.showinfo("Save Recommendations", "No recommendations available to save.")
            return
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Recommendations As...",
                initialfile="mood_recommendations.txt"
            )
            if not file_path: return # User cancelled
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Mood-Based Song Recommendations:\n")
                f.write("="*30 + "\n")
                for idx, song in enumerate(self.current_recommendations, 1):
                    # Write title, artist, and the actual URL
                    f.write(f"{idx}. {song['title']} by {song['artist']}\n")
                    f.write(f"   URL: {song['url']}\n\n") # Include URL directly
                f.write("="*30 + "\n")
            messagebox.showinfo("Save Recommendations", f"Recommendations saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save recommendations:\n{e}")
            print(f"Error saving recommendations: {e}")
    # --- End Save Method ---

    def start_scan(self):
        recommend_limit = self.get_validated_limit()
        # --- Disable both buttons, clear log and stored recs ---
        self.scan_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled") # Disable save button
        self.current_recommendations = [] # Clear stored recommendations
        self.log(f"Starting scan (limit: {recommend_limit})...", clear=True)

        def background_task(limit_to_get):
            # --- Add schedule helper for save button ---
            def schedule_log_update(msg): self.after(0, lambda m=msg: self.log(m))
            def schedule_scan_button_update(state): self.after(0, lambda s=state: self.scan_btn.configure(state=s))
            def schedule_save_button_update(state): self.after(0, lambda s=state: self.save_btn.configure(state=s)) # Added

            img_path = None; final_scan_button_state = "disabled"; final_save_button_state = "disabled"
            recommendations_found = False # Flag
            try:
                schedule_log_update("Capturing image... Press 's' or ESC.")
                img_path = capture_face_image()
                if img_path is None: schedule_log_update("Image capture cancelled."); final_scan_button_state = "normal"; return

                schedule_log_update("Image captured. Detecting mood...")
                mood = detect_mood(img_path)
                if not mood: schedule_log_update("Mood detection failed."); final_scan_button_state = "normal"; return

                schedule_log_update(f"Detected Mood: {mood}\nFinding up to {limit_to_get} recommendations from {CSV_FILENAME}...")
                recs = recommend_songs_by_mood_csv(mood, limit=limit_to_get)

                if not recs: schedule_log_update("No matching songs found.")
                else:
                    # --- Store recommendations ---
                    self.current_recommendations = recs
                    recommendations_found = True
                    # --- Log recommendations (plain text) ---
                    schedule_log_update(f"Top {len(recs)} Recommendations:\n" + "="*20)
                    for idx, song in enumerate(recs, 1):
                        # Log title, artist, and URL plainly
                        log_msg = f"{idx}. {song['title']} by {song['artist']} (URL: {song['url']})"
                        schedule_log_update(log_msg)
                    schedule_log_update("="*20 + "\nScan complete.")
                final_scan_button_state = "normal"
                # --- Enable save button only if recs found ---
                final_save_button_state = "normal" if recommendations_found else "disabled"

            except Exception as e: error_msg = f"Error during scan: {e}"; print(error_msg); schedule_log_update(f"ERROR: {error_msg}"); final_scan_button_state = "normal"
            finally:
                # --- Update both buttons ---
                if songs_df is None: final_scan_button_state = "disabled" # Keep scan disabled if dataset error
                schedule_scan_button_update(final_scan_button_state)
                schedule_save_button_update(final_save_button_state) # Update save button state
                # --- Cleanup ---
                if img_path and os.path.exists(img_path):
                    try: os.remove(img_path); print(f"Cleaned up {img_path}")
                    except OSError as e: print(f"Error removing temp image {img_path}: {e}")

        threading.Thread(target=background_task, args=(recommend_limit,), daemon=True).start()

    # --- Simplified Log function ---
    def log(self, msg, clear=False):
        """Logs a plain text message."""
        try:
            self.output_box.configure(state="normal")
            if clear:
                self.output_box.delete("1.0", ctk.END)
            self.output_box.insert(ctk.END, msg + "\n")
            self.output_box.see(ctk.END)
            self.output_box.configure(state="disabled") # Disable editing
        except Exception as e:
            print(f"Error updating log box: {e}")
    # --- End Simplified Log function ---

if __name__ == '__main__':
    app = MoodRecommenderApp()
    app.mainloop()
