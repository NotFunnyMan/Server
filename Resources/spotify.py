import spotipy
import spotipy.util as util
import os
import json
import pprint

username = 'pva55ddk3p2lm234s5yhh2dyl'
scope = 'user-follow-read'

SPOTIPY_CLIENT_ID = 'aeb7e5af5a5545b188741217cf2f447a'
SPOTIPY_CLIENT_SECRET = '8788d5b6f2c243448698e5424e81b0ed'
SPOTIPY_REDIRECT_URI = 'https://google.com/'

# Get the token
try:
    token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

# Create Spotify instance
sp = spotipy.Spotify(auth=token)

# Get all artists which I follow
result = sp.current_user_followed_artists()
artists = result['artists']['items']
while result['artists']['next']:
    result = sp.next(result['artists'])
    artists.extend(result['artists']['items'])


# Get artist albums
artist_albums = {}  # artist_id: albums_list
for artist in artists:
    result = sp.artist_albums(artist['id'])
    artist_albums[artist['id']] = result['items']

pprint.pprint(artist_albums)



# result = sp.current_user_followed_artists(after=None)
# result = sp.artist_albums('6zNJCgmbt1BbC9d9HWPaHx')  # Egor Nuts
# print(json.dumps(result, indent=4))

# result = sp.album_tracks('2DRxLSdoLRmAOMMbe4UymY')
# print(json.dumps(result, indent=4))

# result = sp.artist_albums('718COspgdWOnwOFpJHRZHS')
# print(json.dumps(result, indent=4))
