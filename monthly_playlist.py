import os
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read playlist-modify-private playlist-modify-public"
    )
)

# Get current month and playlist metadata
now = datetime.datetime.now()
month_name = now.strftime("%B %Y")        
month_id = f"{now.year}{now.month:02}" 
playlist_name = f"{month_name} – Monthly Mix"

user_id = sp.current_user()["id"]
playlist_file = "monthly_playlist_ids.txt"
playlist_id = None

# Check if playlist for this month exists
if os.path.exists(playlist_file):
    with open(playlist_file, "r") as f:
        for line in f:
            if line.startswith(month_id):
                playlist_id = line.strip().split(":")[1]
                print(f"Found existing playlist for {month_name} with ID {playlist_id}")
                break

# Fetch all Liked Songs added this month
current_year = now.year
current_month = now.month
track_uris = []

limit = 50
offset = 0

while True:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    if not results["items"]:
        break

    for item in results["items"]:
        added_at = datetime.datetime.fromisoformat(item["added_at"][:-1])
        if added_at.year == current_year and added_at.month == current_month:
            track_uris.append(item["track"]["uri"])

    offset += limit
    if len(results["items"]) < limit:
        break

# Remove duplicates
track_uris = list(set(track_uris))

if not track_uris:
    print(f"No Liked Songs added this month. Exiting.")
    exit()


# Create playlist
if not playlist_id:
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=f"Automatically generated playlist for {month_name}"
    )
    playlist_id = playlist["id"]

    # Save month_id:playlist_id in file
    with open(playlist_file, "a") as f:
        f.write(f"{month_id}:{playlist_id}\n")
    print(f"Created new playlist '{playlist_name}'.")

# Fetch existing tracks in playlist
existing_tracks = []
limit = 100
offset = 0

while True:
    playlist_items = sp.playlist_items(playlist_id, limit=limit, offset=offset)
    if not playlist_items["items"]:
        break
    existing_tracks.extend([item["track"]["uri"] for item in playlist_items["items"]])
    offset += limit
    if len(playlist_items["items"]) < limit:
        break

#Filter out tracks already in playlist
new_tracks = [uri for uri in track_uris if uri not in existing_tracks]

if not new_tracks:
    print(f"All tracks for {month_name} are already in the playlist. Nothing to add.")
    exit()

# Print tack names
if track_uris:
    print(f"Tracks to add ({len(track_uris)}):")
    for uri in track_uris:
        track_info = sp.track(uri)
        print("-", track_info["name"], "by", ", ".join([a["name"] for a in track_info["artists"]]))
else:
    print(f"No Liked Songs added in {month_name}. Nothing to add.")
    exit()

# Add tracks to the playlist
sp.playlist_add_items(playlist_id, track_uris)
print(f"Added {len(track_uris)} tracks to playlist '{playlist_name}'.")






