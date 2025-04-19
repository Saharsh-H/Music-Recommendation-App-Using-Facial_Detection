import cv2
from deepface import DeepFace
import json
import random

# Load the local song database
def load_song_database(path="songs.json"):
    with open(path, "r") as f:
        return json.load(f)

# Recommend songs by matching mood to tags
def recommend_songs(mood, songs_db, limit=5):
    mood = mood.lower()
    matching_songs = [song for song in songs_db if mood in song["tags"]]
    if not matching_songs:
        print("No direct matches found. Showing random songs instead.")
        return random.sample(songs_db, k=min(limit, len(songs_db)))
    return random.sample(matching_songs, k=min(limit, len(matching_songs)))

# Capture image from webcam
def capture_face(filename="captured_face.jpg"):
    cap = cv2.VideoCapture(0)
    print("Press 's' to scan your face.")
    while True:
        ret, frame = cap.read()
        cv2.imshow("Press 's' to capture", frame)
        if cv2.waitKey(1) & 0xFF == ord("s"):
            cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return filename

# Analyze mood using DeepFace
def detect_mood(image_path):
    print("Analyzing mood...")
    try:
        analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        mood = analysis[0]["dominant_emotion"]
        print(f"Detected Mood: {mood}")
        return mood
    except Exception as e:
        print("Error in mood detection:", e)
        return None

# Main
def main():
    songs_db = load_song_database()
    face_image = capture_face()
    mood = detect_mood(face_image)
    if mood:
        recommendations = recommend_songs(mood, songs_db)
        print("\n🎵 Recommended Songs:")
        for song in recommendations:
            print(f"- {song['title']} by {song['artist']}")

if __name__ == "__main__":
    main()
