import requests
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import os
import time
import json
# import pprint
import time

username = 'pva55ddk3p2lm234s5yhh2dyl'
scope = 'user-follow-read'

SPOTIPY_CLIENT_ID = 'aeb7e5af5a5545b188741217cf2f447a'
SPOTIPY_CLIENT_SECRET = '8788d5b6f2c243448698e5424e81b0ed'
SPOTIPY_REDIRECT_URI = 'https://google.com/'

DELAY_API_REQUEST = 1
DELAY_BTW_GET_UPDATES = 300


def get_conf():
    try:
        with open('spotify_conf.json') as f:
            return json.load(f)
    except Exception as e:
        print(e)


conf = get_conf()


def get_compositions(artist_id, album_group, connector, limit=None):
    artist_compositions = []
    try:
        compositions = connector.artist_albums(artist_id, album_type=album_group)
        artist_compositions.extend(compositions['items'])
        if limit is None:
            limit = compositions['total']
        while compositions['next']:
            if len(artist_compositions) < limit:
                compositions = connector.next(compositions)
                artist_compositions.extend(compositions['items'])
            elif len(artist_compositions) >= limit:
                return artist_compositions[:limit]
    except Exception as e:
        print(e)
    return artist_compositions[:limit]


try:
    token = util.prompt_for_user_token(username,
                                   scope=conf['SPOTIPY_SCOPE'],
                                   client_id=conf['SPOTIPY_CLIENT_ID'],
                                   client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                   redirect_uri=conf['SPOTIPY_REDIRECT_URI'])
except Exception as e:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username,
                                       scope=conf['SPOTIPY_SCOPE'],
                                       client_id=conf['SPOTIPY_CLIENT_ID'],
                                       client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                       redirect_uri=conf['SPOTIPY_REDIRECT_URI'])

sp = spotipy.Spotify(auth=token)

start_time = time.time()
test = get_compositions(artist_id='22bE4uQ6baNwSHPVcDxLCe', album_group='album', limit=1000, connector=sp)
print(time.time() - start_time)
print(len(test))


