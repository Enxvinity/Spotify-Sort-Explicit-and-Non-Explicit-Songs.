import spotipy
from spotipy.oauth2 import SpotifyOAuth

def create_playlist(sp, playlist_name):
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    return playlist["id"]

def add_tracks_to_playlist(sp, playlist_id, track_uris):
    # Add tracks in batches of 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        sp.playlist_add_items(playlist_id, batch)

def get_explicit_tracks(sp, playlist_id):
    explicit_tracks = []

    # Initial request
    results = sp.playlist_tracks(playlist_id)

    # Extract track information from the first page
    playlist_tracks = [{"name": item["track"]["name"], "uri": item["track"]["uri"]} for item in results["items"]]
    explicit_tracks.extend([track_info for track_info in playlist_tracks if sp.track(track_info["uri"])["explicit"]])

    # Continue with pagination
    while results['next']:
        results = sp.next(results)
        playlist_tracks = [{"name": item["track"]["name"], "uri": item["track"]["uri"]} for item in results["items"]]
        explicit_tracks.extend([track_info for track_info in playlist_tracks if sp.track(track_info["uri"])["explicit"]])

    return explicit_tracks


# Set up Spotify API connection
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="your_redirect_uri",
        scope="playlist-read-private,playlist-modify-private,playlist-modify-public,user-library-read",
    )
)

# Specify the name of the playlist you want to extract explicit songs from
playlist_name = "Your Playlist Name"

# Get the specified playlist ID
playlist_id = None
playlists = sp.current_user_playlists()
for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        break

# Check if the playlist was found
if playlist_id:
    # Get explicit tracks from the playlist
    explicit_tracks = get_explicit_tracks(sp, playlist_id)

    # Create a new playlist for explicit tracks
    new_playlist_name = f"Explicit {playlist_name}"
    new_playlist_id = create_playlist(sp, new_playlist_name)

    # Add explicit tracks to the new playlist
    track_uris = [track_info["uri"] for track_info in explicit_tracks]
    add_tracks_to_playlist(sp, new_playlist_id, track_uris)

    print(f"Explicit tracks from '{playlist_name}' added to the '{new_playlist_name}' playlist.")
else:
    print(f"Playlist '{playlist_name}' not found.")
