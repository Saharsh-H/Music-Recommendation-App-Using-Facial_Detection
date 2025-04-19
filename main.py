import random
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Spotify Setup ---
SPOTIFY_CLIENT_ID = '1319252fa7ac404ebbfa10aefd5329a0'
SPOTIFY_CLIENT_SECRET = 'c4403e64a77447d0958420a1498be20e'

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# --- Mood-to-Genre and Valence Mapping ---
mood_genre_map = {
    'happy': ['happy', 'dance', 'edm'],
    'sad': ['sad', 'acoustic', 'blues'],
    'angry': ['metal', 'hard-rock', 'rock'],
    'surprise': ['electronic', 'indie', 'alternative'],
    'fear': ['ambient', 'minimal-techno'],
    'disgust': ['garage', 'grunge', 'punk-rock'],
    'neutral': ['classical', 'ambient', 'chill']
}

# Target valence values for emotions
valence_map = {
    'happy': 0.9,
    'sad': 0.2,
    'angry': 0.3,
    'surprise': 0.7,
    'fear': 0.1,
    'disgust': 0.2,
    'neutral': 0.5
}

# --- Mood Detection ---
def detect_mood(image_path: str) -> str:
    """
    Analyze the image and return the dominant emotion.
    """
    try:
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            enforce_detection=False
        )
        mood = analysis[0]['dominant_emotion'].lower()
        print(f"[INFO] Detected mood: {mood}")
        return mood
    except Exception as e:
        print(f"[ERROR] Mood detection failed: {e}")
        return 'neutral'

# --- Recommendation Logic ---
def get_songs_for_mood(mood: str, limit: int = 5) -> list:
    """
    Fetch recommended tracks from Spotify based on the given mood,
    filter by audio feature valence, and return top `limit` songs with
    title, cover image URL, and Spotify link.
    """
    # Choose genres and target valence
    genres = mood_genre_map.get(mood, ['pop'])
    target_valence = valence_map.get(mood, 0.5)
    seed_genre = random.choice(genres)
    print(f"[INFO] Using seed genre: {seed_genre}, target valence: {target_valence}")

    # Get raw recommendations (fetch extra for filtering)
    raw = sp.recommendations(seed_genres=[seed_genre], limit=limit * 3)
    tracks = raw.get('tracks', [])

    # Score by closeness to target valence + energy
    scored = []
    for track in tracks:
        feat = sp.audio_features(track['id'])[0]
        if feat:
            valence_diff = abs(feat['valence'] - target_valence)
            energy_diff = abs(feat['energy'] - 0.5)  # secondary filter
            score = valence_diff + energy_diff
            scored.append((score, track))

    # Sort and select top
    scored.sort(key=lambda x: x[0])
    selected = [t for _, t in scored[:limit]]

    # Format output with title, cover image, and link
    recommendations = []
    for t in selected:
        title = t['name']
        cover_url = ''
        # Extract first cover image if available
        if t.get('album') and t['album'].get('images'):
            cover_url = t['album']['images'][0]['url']
        spotify_link = t['external_urls']['spotify']
        recommendations.append({
            'title': title,
            'cover_url': cover_url,
            'url': spotify_link
        })

    return recommendations

# --- For direct invocation ---
if __name__ == '__main__':
    import sys
    from utils import capture_face_image

    image_path = sys.argv[1] if len(sys.argv) > 1 else capture_face_image()
    mood = detect_mood(image_path)
    recs = get_songs_for_mood(mood)
    print("\n🎵 Recommendations:")
    for s in recs:
        print(f"- {s['title']}\n  Cover: {s['cover_url']}\n  Link: {s['url']}\n")
