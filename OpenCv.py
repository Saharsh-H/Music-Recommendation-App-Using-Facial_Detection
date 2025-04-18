import cv2
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

# # --- Spotify Setup ---
# SPOTIFY_CLIENT_ID = '1319252fa7ac404ebbfa10aefd5329a0'
# SPOTIFY_CLIENT_SECRET = 'c4403e64a77447d0958420a1498be20e'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='1319252fa7ac404ebbfa10aefd5329a0',
    client_secret='c4403e64a77447d0958420a1498be20e'
))

try:
    print("Fetching available genres from Spotify...")
    print(sp.recommendation_genre_seeds())
except spotipy.exceptions.SpotifyException as e:
    print("Error fetching genre seeds:", e)


# --- Mood to Genre Mapping ---
mood_genre_map = {
    'happy': ['happy', 'dance', 'edm'],
    'sad': ['sad', 'acoustic', 'blues'],
    'angry': ['metal', 'hard-rock', 'rock'],
    'surprise': ['electronic', 'indie', 'alternative'],
    'fear': ['ambient', 'minimal-techno'],
    'disgust': ['garage', 'grunge', 'punk-rock'],
    'neutral': ['classical', 'ambient', 'chill']
}




# --- Capture Face ---
def capture_face_image():
    cap = cv2.VideoCapture(0)
    print("Press 's' to scan your face.")

    while True:
        ret, frame = cap.read()
        cv2.imshow('Mood Scanner - Press "s" to scan', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            img_path = 'captured_face.jpg'
            cv2.imwrite(img_path, frame)
            break

    cap.release()
    cv2.destroyAllWindows()
    return img_path

# --- Analyze Mood ---
def detect_mood(image_path):
    print("Analyzing mood...")
    result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
    mood = result[0]['dominant_emotion']
    print(f"Detected Mood: {mood}")
    return mood

# --- Get Songs Based on Mood ---
def get_songs_for_mood(mood, limit=5):
    genres = mood_genre_map.get(mood.lower(), ['pop'])
    chosen_genre = random.choice(genres)
    print(f"Fetching songs in genre: {chosen_genre}")

    results = sp.recommendations(seed_genres=[chosen_genre], limit=limit)
    songs = []
    for track in results['tracks']:
        name = track['name']
        artist = track['artists'][0]['name']
        url = track['external_urls']['spotify']
        songs.append(f"{name} by {artist} → {url}")
    return songs

# --- Main ---
if __name__ == "__main__":
    image_path = capture_face_image()
    mood = detect_mood(image_path)
    recommendations = get_songs_for_mood(mood)
    
    print("\n🎵 Recommended Songs:")
    for song in recommendations:
        print(song)
