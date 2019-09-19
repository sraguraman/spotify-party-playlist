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
redirect_uri = config.get('SPOTIFY', 'REDIRECT_URI')

auth = oauth2.SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def get_info():
    new_playlist_name = request.form['new-playlist']
    user_username = request.form['user-username']
    user_playlist = request.form['user-playlist']
    friend_one_username = request.form['first-guest-username']
    friend_one_playlist = request.form['first-guest-playlist']
    friend_two_username = request.form['second-guest-username']
    friend_two_playlist = request.form['second-guest-playlist']
    top_forty = request.form['top-40-selection']

    token = util.prompt_for_user_token(user_username, 'playlist-modify-public', redirect_uri)
    spotify = spotipy.Spotify(auth=token)

    # creating new playlist for user 
    playlist_description = "A playlist combining you and your friends' favorite music!"
    spotify.user_playlist_create(user_username, new_playlist_name, playlist_description)


    # compiling songs from all users into one playlist
    all_usernames_and_playlists = {}
    all_usernames.append((user_username, user_playlist), (friend_one_username, friend_one_playlist), (friend_two_username, friend_two_playlist))
    user_public_playlists = spotify.user_playlists(user_username)
    for playlist in user_public_playlists:
        if new_playlist_name == playlist['name']:
            user_playlist_id = playlist["id"]
            break

    for username, playlist_name in all_usernames_and_playlists.items:
        all_public_playlists = spotify.user_playlists(username)
        for playlist in all_public_playlists:
            if playlist_name == playlist['name']:
                current_playlist_id = playlist["id"]
                break
        results = spotify.user_playlist_tracks(username, current_playlist_id)
        playlist_items = results['items']
        uris = []

        while results['next']:
            results = spotify.next(results)
            playlist_items.append(results['items'])
        
        for item in playlist_items:
            is_local = item["is_local"]
            if is_local == True:
                continue #skips if track is local
            else:
                track_uri = item["track"]["uri"]
                uris.append(track_uri)

        spotify.user_playlist_add_tracks(user_username, user_playlist_id, uris)

    return redirect('https://open.spotify.com/collections/playlists')