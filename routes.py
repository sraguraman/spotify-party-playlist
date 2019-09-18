from app import app
from flask import render_template, jsonify

import spotipy 
import spotipy.util as util 
import spotipy.oauth2 as oauth2
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
client_id = config.get('SPOTIFY', 'CLIENT_ID')
client_secret = config.get('SPOTIFY', 'CLIENT_SECRET')

auth = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

token = auth.get_access_token()
spotify = spotipy.Spotify(auth=token)

@app.route('/')
@app.route('/index')
def index():
    username = "127904618"
    playlists = spotify.user_playlists(username)
    playlist_names = []
    for playlist in playlists['items']:
        playlist_names.append(playlist['name'])
    return render_template('index.html')
