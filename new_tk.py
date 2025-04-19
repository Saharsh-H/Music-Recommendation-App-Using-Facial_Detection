import customtkinter as ctk
from tkinter import messagebox, simpledialog
import cv2
from deepface import DeepFace
import webbrowser
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import threading

# --- Configuration ---
CLIENT_ID = '1319252fa7ac404ebbfa10aefd5329a0'
CLIENT_SECRET = 'c4403e64a77447d0958420a1498be20e'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'user-library-read'

# --- Recommend Songs Using Spotify Search ---
def recommend_songs_by_mood(mood, sp_client, limit=5):
    mood = mood.lower()

    mood_tags = {
        "happy": ["feel-good", "upbeat", "summer", "fun", "party"],
        "sad": ["melancholy", "heartbreak", "emotional", "soft", "slow"],
        "angry": ["aggressive", "rock", "rage", "metal", "intense"],
        "neutral": ["chill", "relaxing", "ambient", "vibe", "lofi"],
        "fear": ["dark", "cinematic", "tense", "moody", "haunting"],
        "surprise": ["experimental", "quirky", "unexpected", "fusion", "alt"],
        "disgust": ["grunge", "raw", "underground", "rebellious"]
    }

    tags = mood_tags.get(mood, ["pop"])
    recommendations = []
    for tag in tags:
        result = sp_client.search(q=tag, type='track', limit=limit)
        for item in result.get('tracks', {}).get('items', []):
            recommendations.append({
                'title': item['name'],
                'artist': item['artists'][0]['name'],
                'preview_url': item.get('preview_url'),
                'spotify_url': item['external_urls']['spotify']
            })
        if len(recommendations) >= limit:
            break
    return recommendations[:limit]

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
class SpotifyMoodApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Mood Recommender")
        self.geometry("600x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.sp = None

        self.auth_btn = ctk.CTkButton(self, text="Authenticate Spotify", command=self.auth_flow)
        self.auth_btn.pack(pady=10)

        self.scan_btn = ctk.CTkButton(self, text="Scan Mood & Recommend", state="disabled", command=self.start_scan)
        self.scan_btn.pack(pady=10)

        self.output_box = ctk.CTkTextbox(self, width=560, height=300)
        self.output_box.pack(padx=20, pady=20)
        self.output_box.configure(state="disabled")

    def auth_flow(self):
        self.auth_btn.configure(state="disabled")
        self.output_box.configure(state="normal")
        self.output_box.delete(1.0, ctk.END)
        self.output_box.insert(ctk.END, "Opening browser for Spotify authentication...\n")
        self.output_box.configure(state="disabled")

        oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        )
        auth_url = oauth.get_authorize_url()
        webbrowser.open(auth_url)

        # Get user input on main thread
        self.after(100, lambda: self.get_user_input(oauth))

    def get_user_input(self, oauth):
        redirect_response = simpledialog.askstring("Spotify Auth", "Paste the full redirect URL after authorization:")
        if not redirect_response:
            messagebox.showerror("Error", "Authorization URL not provided.")
            self.auth_btn.configure(state="normal")
            return

        def finish_auth():
            try:
                code = oauth.parse_response_code(redirect_response)
                token_info = oauth.get_access_token(code)
                self.sp = Spotify(auth=token_info['access_token'])
                self.output_box.configure(state="normal")
                self.output_box.insert(ctk.END, "Authentication successful! You can now scan.\n")
                self.output_box.configure(state="disabled")
                self.scan_btn.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Auth Error", str(e))
                self.output_box.configure(state="normal")
                self.output_box.insert(ctk.END, f"Authentication failed: {e}\n")
                self.output_box.configure(state="disabled")
                self.auth_btn.configure(state="normal")

        threading.Thread(target=finish_auth, daemon=True).start()

    def start_scan(self):
        self.scan_btn.configure(state="disabled")
        self.output_box.configure(state="normal")
        self.output_box.delete(1.0, ctk.END)
        self.output_box.insert(ctk.END, "Capturing image... Press 's' in the camera window.\n")
        self.output_box.configure(state="disabled")

        def scan_flow():
            try:
                img_path = capture_face_image()
                mood = detect_mood(img_path)
                if not mood:
                    raise ValueError("No mood detected.")
                recs = recommend_songs_by_mood(mood, self.sp)

                self.output_box.configure(state="normal")
                self.output_box.delete(1.0, ctk.END)
                self.output_box.insert(ctk.END, f"Detected Mood: {mood}\n\nRecommendations:\n")
                for idx, t in enumerate(recs, 1):
                    self.output_box.insert(ctk.END, f"{idx}. {t['title']} by {t['artist']}\n")
                    if t['preview_url']:
                        self.output_box.insert(ctk.END, f"   Preview: {t['preview_url']}\n")
                    self.output_box.insert(ctk.END, f"   Link: {t['spotify_url']}\n\n")
                self.output_box.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.output_box.configure(state="normal")
                self.output_box.insert(ctk.END, f"Error: {e}\n")
                self.output_box.configure(state="disabled")
            finally:
                self.scan_btn.configure(state="normal")

        threading.Thread(target=scan_flow, daemon=True).start()

if __name__ == '__main__':
    app = SpotifyMoodApp()
    app.mainloop()
