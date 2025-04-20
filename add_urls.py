import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ast  # For safely evaluating the string list of artists
import os
import time # To add delays between API calls

# --- Configuration ---
INPUT_CSV_FILENAME = 'Songs Dataset.csv'
OUTPUT_CSV_FILENAME = 'Songs_Dataset_with_URLs.csv'
# Assumed column names based on your CSV structure
TITLE_COLUMN = 'name'
ARTIST_COLUMN = 'artists'

# --- Spotify API Setup ---
# !!! IMPORTANT: Using hardcoded credentials below as requested. !!!
# !!! Consider using environment variables for better security in the future. !!!

# --- Credentials provided by user ---
SPOTIFY_CLIENT_ID = 'd08bd26e9a2f4189821e1068d389d255' # <-- User's Client ID
SPOTIFY_CLIENT_SECRET = '4f52b67ad42a4d66a142a9edc4891bc2' # <-- User's Client Secret
# --- End Credentials Section ---


sp = None
try:
    
    if 'YOUR_CLIENT_ID_HERE' in SPOTIFY_CLIENT_ID or 'YOUR_CLIENT_SECRET_HERE' in SPOTIFY_CLIENT_SECRET:
         raise ValueError("Placeholder check failed unexpectedly - this shouldn't happen now.")
    # --- End Corrected Check ---

    # If the check passes, proceed normally:
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    print("Successfully connected to Spotify API.")
except Exception as e:
    print(f"Error initializing Spotify: {e}")
    print("Please ensure spotipy is installed and credentials are correct.")
    sp = None

# --- Helper Functions ---
def parse_artist(artist_str):
    """Safely parses the first artist from the string representation."""
    try:
        artists_list = ast.literal_eval(artist_str)
        if isinstance(artists_list, list) and artists_list:
            return artists_list[0]
    except (ValueError, SyntaxError, TypeError) as e:
        pass
    return None

def get_spotify_url(sp_client, title, artist):
    """Searches Spotify for a track and returns its URL."""
    if not sp_client or not title or not artist:
        return None

    try:
        query = f"track:{title} artist:{artist}"
        results = sp_client.search(q=query, type='track', limit=1)

        if results and results['tracks'] and results['tracks']['items']:
            track = results['tracks']['items'][0]
            url = track.get('external_urls', {}).get('spotify')
            return url
        else:
            return None
    except spotipy.exceptions.SpotifyException as e:
        print(f"  - Spotify API Error searching for '{title}': {e}")
        if e.http_status == 429:
            print("  - Rate limit hit. Waiting...")
            time.sleep(5)
            return "RATE_LIMIT_RETRY"
        return None
    except Exception as e:
        print(f"  - Unexpected error searching for '{title}': {e}")
        return None

# --- Main Script Logic ---
if sp:
    print(f"Reading input CSV: {INPUT_CSV_FILENAME}")
    try:
        df = pd.read_csv(INPUT_CSV_FILENAME)
    except FileNotFoundError:
        print(f"ERROR: Input file '{INPUT_CSV_FILENAME}' not found.")
        exit()
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        exit()

    if TITLE_COLUMN not in df.columns or ARTIST_COLUMN not in df.columns:
        print(f"ERROR: Required columns '{TITLE_COLUMN}' or '{ARTIST_COLUMN}' not found in CSV.")
        exit()

    total_rows = len(df)
    print(f"Found {total_rows} songs. Starting URL search...")
    urls = []
    processed_count = 0

    for index, row in df.iterrows():
        title = row[TITLE_COLUMN]
        artist_str = row[ARTIST_COLUMN]

        if pd.isna(title) or not isinstance(title, str):
            title = None
        if pd.isna(artist_str) or not isinstance(artist_str, str):
            artist_str = None
            artist = None
        else:
             artist = parse_artist(artist_str)

        print(f"Processing {index + 1}/{total_rows}: '{title or 'N/A'}' by '{artist or 'N/A'}'...")

        url = None
        if title and artist:
            url = get_spotify_url(sp, title, artist)
            while url == "RATE_LIMIT_RETRY":
                 print(f"Retrying {index + 1}/{total_rows} after rate limit delay...")
                 time.sleep(1)
                 url = get_spotify_url(sp, title, artist)

        urls.append(url if url else '')
        processed_count += 1
        time.sleep(0.1)

    print(f"\nURL search complete. Processed {processed_count} rows.")
    df['url'] = urls

    try:
        df.to_csv(OUTPUT_CSV_FILENAME, index=False, encoding='utf-8')
        print(f"Successfully saved updated data to: {OUTPUT_CSV_FILENAME}")
    except Exception as e:
        print(f"ERROR: Failed to save output CSV: {e}")

else:
    print("Spotify client failed to initialize. Cannot proceed.")

