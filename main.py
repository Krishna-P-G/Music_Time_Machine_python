import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import YOUR_APP_CLIENT_ID,YOUR_APP_CLIENT_SECRET,YOUR_APP_REDIRECT_URI,YOUR_APP_CLIENT_USERNAME
from bs4 import BeautifulSoup
import requests

"""Authentication of spotify"""
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=YOUR_APP_REDIRECT_URI,
        client_id=YOUR_APP_CLIENT_ID,
        client_secret=YOUR_APP_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
        username=YOUR_APP_CLIENT_USERNAME,
    )
)


def get_spotify_uri(song, release):
    """This function is for getting the spotify_uri"""
    results = sp.search(q=f"track:{song} year:{release}", type="track")

    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    else:
        return None


def create_private_playlist(name, user):
    """this function is for creating a new private playlist"""
    playlist = sp.user_playlist_create(user, name, public=False, collaborative=False, description="Billboard 100 Playlist")
    return playlist["id"]


def get_playlist_info(name, user):
    playlists = sp.user_playlists(user)
    for playlist in playlists["items"]:
        if playlist["name"] == name:
            return playlist["id"], sp.playlist_tracks(playlist["id"])["items"]
    return None, None


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")

URL = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(URL)
time_music = response.text
soup = BeautifulSoup(time_music, "html.parser")
all_music = soup.select(selector="li ul li h3")
music_list = []

for music in all_music:
    title = music.getText()
    music_list.append(title)

for i in range(len(music_list)):
    music_list[i] = music_list[i].strip()

user_id = sp.current_user()["id"]

spotify_uris = []

playlist_name = f"{date} Billboard 100"
playlist_id, existing_track_uris = get_playlist_info(playlist_name, user_id)
if existing_track_uris is None:
    existing_track_uris = []

if not playlist_id:
    # Playlist doesn't exist, so create it
    playlist_id = create_private_playlist(playlist_name, user_id)
    print(f"Created a new private playlist: {playlist_name} (ID: {playlist_id})")
else:
    print(f"The playlist '{playlist_name}' already exists (ID: {playlist_id})")


for song_name in music_list:
    release_date = date
    release_year = int(release_date.split("-")[0])
    uri = get_spotify_uri(song_name, release_year)

    if uri:
        if uri not in existing_track_uris:
            spotify_uris.append(uri)
            existing_track_uris.append(uri)
        else:
            print(f"Song '{song_name}' is already in the playlist and will not be added.")
    else:
        print(f"Could not find the Spotify URI for '{song_name}' released on {release_date}")

if spotify_uris:
    sp.playlist_add_items(playlist_id, spotify_uris)
    print(f"Added {len(spotify_uris)} songs to the playlist.")