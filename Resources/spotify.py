import spotipy
import spotipy.util as util
import os
import json

username = 'pva55ddk3p2lm234s5yhh2dyl'
scope = 'user-follow-read'

SPOTIPY_CLIENT_ID = 'aeb7e5af5a5545b188741217cf2f447a'
SPOTIPY_CLIENT_SECRET = '8788d5b6f2c243448698e5424e81b0ed'
SPOTIPY_REDIRECT_URI = 'https://google.com/'


try:
    token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)


sp = spotipy.Spotify(auth=token)
results = sp.current_user()
print(json.dumps(results, sort_keys=True, indent=4))
