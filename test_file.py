import requests
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import os
import time
# import json
# import pprint

username = 'pva55ddk3p2lm234s5yhh2dyl'
scope = 'user-follow-read'

SPOTIPY_CLIENT_ID = 'aeb7e5af5a5545b188741217cf2f447a'
SPOTIPY_CLIENT_SECRET = '8788d5b6f2c243448698e5424e81b0ed'
SPOTIPY_REDIRECT_URI = 'https://google.com/'

DELAY_API_REQUEST = 1
DELAY_BTW_GET_UPDATES = 300



test = oauth2.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope)

# Create Spotify instance
auth_url = test.get_authorize_url()
res = requests.post(auth_url, allow_redirects=True)
resp_code = test.parse_response_code(auth_url)
token = test.get_access_token(resp_code)

sp = spotipy.Spotify(auth=token['access_token'])
result = sp.current_user_followed_artists()
print(result)

