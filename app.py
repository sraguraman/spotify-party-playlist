from flask import Flask, render_template, jsonify, redirect, request
from urllib.parse import quote
from bottle import route, run, request
import requests
import json
import spotipy 
import spotipy.util as util 
import spotipy.oauth2 as oauth2
import configparser
import operator
import os

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')

#Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
PORT = 8080

SCOPE = "playlist-modify-private playlist-modify-public"
redirect_uri = "https://spotify-combined-playlist.herokuapp.com/callback/q"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": SCOPE,
    "client_id": client_id
}

@app.route("/")
def index():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q")
def callback():
    token = request.args.get('code')
    payload = {
        "grant_type": "authorization_code",
        "code": str(token),
        "redirect_uri": redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    
    json_request = requests.post(SPOTIFY_TOKEN_URL, data=payload)

    request_data = json.loads(json_request.text)
    global access_token 
    access_token = request_data["access_token"]
    global auth_header 
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    return render_template('index.html')

@app.route("/#features", methods=['POST'])
def data_wrangle():
    new_playlist_name = request.form['new-playlist']
    user_username = request.form['user-username']
    #user_playlist = request.form['user-playlist']
    friend_one_username = request.form['first-guest-username']
    #friend_one_playlist = request.form['first-guest-playlist']
    friend_two_username = request.form['second-guest-username']
    #friend_two_playlist = request.form['second-guest-playlist']

    usernames = []
    usernames.append(friend_one_username)
    usernames.append(friend_two_username)

    all_songs = {}
    for username in usernames:
        current_playlist = requests.get('https://api.spotify.com/v1/users/' + str(username) + '/playlists', headers=auth_header)
        j_response = current_playlist.json()
        for playlist in j_response['items']:
            p_id = playlist['id']
            songs = requests.get('https://api.spotify.com/v1/users/' + str(username) + '/playlists/' + str(p_id) + '/tracks', headers=auth_header)
            song_data = songs.json()
            for song in song_data['items']:
                if song["track"]["id"] in all_songs:
                    all_songs[song["track"]["id"]] += 1
                else:
                    all_songs[song["track"]["id"]] = 1
    
    reverse = sorted(all_songs.items(), key=operator.itemgetter(1), reverse=True)
    songs = []
    num_songs = 0

    for key in reverse:
        if num_songs < 100:
            song = requests.get('https://api.spotify.com/v1/tracks/' + key, headers=auth_header)
            #song_json = song.json()
            #song_name = song_json['name']
            songs.append(key)
            num_songs += 1
        else:
            break

    spotify = spotipy.Spotify(auth=access_token)
    spotify.user_playlist_create(user_username, str(new_playlist_name))

    new_playlists = requests.get('https://api.spotify.com/v1/users/' + str(user_username) + '/playlists', headers=auth_header)
    playlist_json = new_playlists.json()

    for playlist in playlist_json['items']:
        if playlist['name'] == new_playlist_name:
            spotify.user_playlist_add_tracks(user_username, playlist["id"], all_songs)

    return redirect('https://open.spotify.com/collection/playlists')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host= "0.0.0.0", port=port)
