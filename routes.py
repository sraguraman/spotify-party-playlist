from app import app
from flask import render_template, jsonify, request

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
    return render_template("index.html")

@app.route('/new_playlist', methods=['POST'])
def get_info():
    new_playlist_name = request.form['new-playlist']
    user_username = request.form['user-username']
    user_playlist = request.form['user-playlist']
    friend_one_username = request.form['first-guest-username']
    friend_one_playlist = request.form['first-guest-playlist']
    friend_two_username = request.form['second-guest-username']
    friend_two_playlist = request.form['second-guest-playlist']
    top_forty = request.form['top-40-selection']

    # creating new playlist for user 
    playlist_description = "A playlist combining you and your friends' favorite music!"
    new_playlist = spotify.user_playlist_create(user_username, new_playlist_name, playlist_description)


    return render_template("new_playlist.html",  new_playlist_name=new_playlist_name)
    



