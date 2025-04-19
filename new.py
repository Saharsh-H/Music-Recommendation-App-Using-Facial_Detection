# import cv2
# from deepface import DeepFace
# import json
# import random

# # Load the local song database
# def load_song_database(path="songs.json"):
#     with open(path, "r") as f:
#         return json.load(f)

# # Recommend songs by matching mood to tags
# def recommend_songs(mood, songs_db, limit=5):
#     mood = mood.lower()
#     matching_songs = [song for song in songs_db if mood in song["tags"]]
#     if not matching_songs:
#         print("No direct matches found. Showing random songs instead.")
#         return random.sample(songs_db, k=min(limit, len(songs_db)))
#     return random.sample(matching_songs, k=min(limit, len(matching_songs)))

# # Capture image from webcam
# def capture_face(filename="captured_face.jpg"):
#     cap = cv2.VideoCapture(0)
#     print("Press 's' to scan your face.")
#     while True:
#         ret, frame = cap.read()
#         cv2.imshow("Press 's' to capture", frame)
#         if cv2.waitKey(1) & 0xFF == ord("s"):
#             cv2.imwrite(filename, frame)
#             break
#     cap.release()
#     cv2.destroyAllWindows()
#     return filename

# # Analyze mood using DeepFace
# def detect_mood(image_path):
#     print("Analyzing mood...")
#     try:
#         analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
#         mood = analysis[0]["dominant_emotion"]
#         print(f"Detected Mood: {mood}")
#         return mood
#     except Exception as e:
#         print("Error in mood detection:", e)
#         return None

# # Main
# def main():
#     songs_db = load_song_database()
#     face_image = capture_face()
#     mood = detect_mood(face_image)
#     if mood:
#         recommendations = recommend_songs(mood, songs_db)
#         print("\n🎵 Recommended Songs:")
#         for song in recommendations:
#             print(f"- {song['title']} by {song['artist']}")

# if __name__ == "__main__":
#     main()

# import cv2
# from deepface import DeepFace
# import json
# import random
# import webbrowser
# from spotipy import Spotify
# from spotipy.oauth2 import SpotifyOAuth

# # --- Configuration ---
# CLIENT_ID = '1319252fa7ac404ebbfa10aefd5329a0'
# CLIENT_SECRET = 'c4403e64a77447d0958420a1498be20e'
# REDIRECT_URI = 'http://127.0.0.1:8888/callback'
# SCOPE = 'user-library-read'
# SONG_DB_PATH = 'songs.json'

# # --- Authentication (Authorization Code Flow) ---
# def authenticate_spotify():
#     oauth = SpotifyOAuth(
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE
#     )
#     auth_url = oauth.get_authorize_url()
#     print("\n1) Go to the following URL to authorize:\n", auth_url)
#     print("\n2) After granting access, you will be redirected to a URL. Copy and paste the full redirect URL below.")
#     webbrowser.open(auth_url)
#     response = input("\nPaste redirect URL here: ")
#     code = oauth.parse_response_code(response)
#     token_info = oauth.get_access_token(code)
#     return Spotify(auth=token_info['access_token'])

# # --- Load local song database ---
# def load_song_database(path=SONG_DB_PATH):
#     with open(path, 'r') as f:
#         return json.load(f)

# # --- Recommend songs by local tags and enrich with Spotify data ---
# def recommend_songs(mood, songs_db, sp_client, limit=5):
#     mood = mood.lower()
#     # find matching local entries
#     matches = [s for s in songs_db if mood in s['tags']]
#     if not matches:
#         print("No direct tag matches found. Selecting random songs.")
#         matches = random.sample(songs_db, k=min(limit, len(songs_db)))
#     else:
#         matches = random.sample(matches, k=min(limit, len(matches)))

#     enriched = []
#     for song in matches:
#         query = f"track:{song['title']} artist:{song['artist']}"
#         result = sp_client.search(q=query, type='track', limit=1)
#         items = result.get('tracks', {}).get('items', [])
#         if items:
#             track = items[0]
#             enriched.append({
#                 'title': track['name'],
#                 'artist': track['artists'][0]['name'],
#                 'preview_url': track.get('preview_url'),
#                 'spotify_url': track['external_urls']['spotify']
#             })
#         else:
#             # fallback to local info if Spotify search fails
#             enriched.append({
#                 'title': song['title'],
#                 'artist': song['artist'],
#                 'preview_url': None,
#                 'spotify_url': None
#             })
#     return enriched

# # --- Capture face image ---
# def capture_face_image(filename='captured_face.jpg'):
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#     if not cap.isOpened():
#         print("Error: Could not access the webcam.")
#         return None
#     print("Press 's' to scan your face.")
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         cv2.imshow("Mood Capture", frame)
#         if cv2.waitKey(1) & 0xFF == ord('s'):
#             cv2.imwrite(filename, frame)
#             break
#     cap.release()
#     cv2.destroyAllWindows()
#     return filename

# # --- Detect mood with DeepFace ---
# def detect_mood(image_path):
#     print("Analyzing mood...")
#     try:
#         analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
#         mood = analysis[0]['dominant_emotion']
#         print(f"Detected mood: {mood}")
#         return mood
#     except Exception as e:
#         print(f"Error detecting mood: {e}")
#         return None

# # --- Main Execution ---
# def main():
#     # Authenticate Spotify user
#     sp = authenticate_spotify()

#     # Load songs database
#     songs_db = load_song_database()

#     # Capture face and detect mood
#     img_path = capture_face_image()
#     if not img_path:
#         return
#     mood = detect_mood(img_path)
#     if not mood:
#         return

#     # Recommend and enrich songs
#     recommendations = recommend_songs(mood, songs_db, sp)
#     print("\n🎵 Recommended Tracks 🎵")
#     for idx, track in enumerate(recommendations, 1):
#         title = track['title']
#         artist = track['artist']
#         preview = track['preview_url'] or 'No preview available'
#         url = track['spotify_url'] or 'No Spotify link'
#         print(f"{idx}. {title} by {artist}\n   Preview: {preview}\n   Link: {url}\n")

# if __name__ == '__main__':
#     main()

import cv2
from deepface import DeepFace
import webbrowser
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# --- Configuration ---
CLIENT_ID = '1319252fa7ac404ebbfa10aefd5329a0'
CLIENT_SECRET = 'c4403e64a77447d0958420a1498be20e'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'user-library-read'

# --- Spotify Auth ---
def authenticate_spotify():
    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    auth_url = oauth.get_authorize_url()
    print("\n1) Open this URL to authorize:\n", auth_url)
    webbrowser.open(auth_url)
    response = input("\n2) Paste the redirect URL here: ")
    code = oauth.parse_response_code(response)
    token_info = oauth.get_access_token(code)
    return Spotify(auth=token_info['access_token'])

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


# --- Capture Face ---
def capture_face_image(filename='captured_face.jpg'):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return None
    print("Press 's' to scan your face.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Mood Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return filename

# --- Detect Mood ---
def detect_mood(image_path):
    print("Analyzing mood...")
    try:
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        mood = analysis[0]['dominant_emotion']
        print(f"Detected mood: {mood}")
        return mood
    except Exception as e:
        print(f"Error detecting mood: {e}")
        return None

# --- Main ---
def main():
    sp = authenticate_spotify()
    img_path = capture_face_image()
    if not img_path:
        return
    mood = detect_mood(img_path)
    if not mood:
        return
    recommendations = recommend_songs_by_mood(mood, sp)
    print("\n🎵 Recommended Tracks 🎵")
    for idx, track in enumerate(recommendations, 1):
        title = track['title']
        artist = track['artist']
        preview = track['preview_url'] or 'No preview available'
        url = track['spotify_url'] or 'No Spotify link'
        print(f"{idx}. {title} by {artist}\n   Preview: {preview}\n   Link: {url}\n")

if __name__ == '__main__':
    main()
