import requests
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import os
import time
import json
import pprint
import time
import platform
from spotipy.client import SpotifyException

DELAY_API_REQUEST = 1
DELAY_BTW_GET_UPDATES = 300


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print("%s. Time spent: %s" % (func.__name__, time.time() - start))
        return res
    return wrapper


def check_token(func):
    def wrapper(*args, **kwargs):
        f = open('Cache/.cache-pva55ddk3p2lm234s5yhh2dyl').read()
        f = json.loads(f)
        if oauth2.is_token_expired(f):
            # refresh the token!
            pass
        res = func(*args, **kwargs)
        return res
    return wrapper


def get_conf():
    try:
        file_path = 'Confs/spotify_conf.json' if platform.system() == 'Windows' else 'Confs/spotify_conf.json'
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        print(e)


def get_token(username):
    try:
        token = util.prompt_for_user_token(username,
                                           scope=conf['SPOTIPY_SCOPE'],
                                           client_id=conf['SPOTIPY_CLIENT_ID'],
                                           client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=conf['SPOTIPY_REDIRECT_URI'],
                                           cache_path=conf['CACHE_PATH'].replace('../', '') + ".cache-" + username)
    except Exception as e:
        os.remove(f"{conf['CACHE_PATH']} + .cache-{username}")
        token = util.prompt_for_user_token(username,
                                           scope=conf['SPOTIPY_SCOPE'],
                                           client_id=conf['SPOTIPY_CLIENT_ID'],
                                           client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=conf['SPOTIPY_REDIRECT_URI'],
                                           cache_path=conf['CACHE_PATH'].replace('../', '') + ".cache-" + username)
    return token


@check_token
def get_following_artists(token):
    try:
        result = token.current_user_followed_artists()
        artists = result['artists']['items']
        while result['artists']['next']:
            result = token.next(result['artists'])
            artists.extend(result['artists']['items'])
        return get_latest_compositions(token, artists)
    except SpotifyException as e:
        print(e)
        if e.http_status == 401:
            # token = spotipy.Spotify(auth=get_token())
            # get_following_artists(token)
            print('\n\nSpotifyException! TOKEN HAS BEEN EXPAIRED!\n\n')
    except Exception as e:
        print(e)


@benchmark
def get_latest_compositions(token, artists):
    composition_types = ['album', 'single', 'appears_on', 'compilation']
    for artist in artists:
        for composition in composition_types:
            compos = get_compositions(token, album_group=composition, limit=1, artist_id=artist['id'])
            if compos: del(compos[0]['available_markets'])
            artist['latest_' + composition] = compos[0] if compos != [] else None
    return artists


@check_token
def get_compositions(token, album_group, artist_id, limit=None):
    artist_compositions = []
    try:
        compositions = token.artist_albums(artist_id, album_type=album_group)
        artist_compositions.extend(compositions['items'])
        if limit is None:
            limit = compositions['total']
        while compositions['next']:
            if len(artist_compositions) < limit:
                compositions = token.next(compositions)
                artist_compositions.extend(compositions['items'])
            else:
                break
        return artist_compositions[:limit]
    except SpotifyException as e:
        print(e)
        if e.http_status == 401:
            pass
    except Exception as e:
        print(e)


@benchmark
def db_load(filename):
    filename = 'LocalDB/' + str(filename)
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


@benchmark
def db_dump(data, filename):
    filename = 'LocalDB/' + str(filename)
    if type(data) is not list:
        data = [data]
    if os.path.isfile(filename):
        data_from_json = db_load(filename)
        data_from_json.extend(data)
        data = data_from_json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@benchmark
def initialization(username):
    token = spotipy.Spotify(auth=get_token(username))
    all_artists = dict(username=username)
    all_artists['artists'] = get_following_artists(token)
    return all_artists


@benchmark
def _dump_artist_user(artists, username):
    res = []
    for artist in artists:
        data = dict(id=artist['id'], name=artist['name'])
        res.append(data)
    d = dict(username=username, artists=res)
    db_dump(d, 'user_artists.json')


@benchmark
def _find_user_in_db_data(data, username):
    for dat in data:
        if dat['username'] == username:
            return dat


@benchmark
def _find_artist_in_db_data(artists, artist_id):
    for artist in artists['artists']:
        if artist['id'] == artist_id:
            return artist


def _compare_two_compositions(init, new):
    if init is None:
        if len(new) != 0:
            return True
        else:
            return False
    elif len(new) != 0:
        return init['id'] != new[0]['id']


@benchmark
def check_updates():
    users = db_load('user_artists.json')
    db_data = db_load('initialize.json')
    for user in users:
        token = spotipy.Spotify(auth=get_token(user['username']))
        db_data = _find_user_in_db_data(db_data, user['username'])
        user_artists = user['artists']
        for user_artist in user_artists:
            composition_types = ['album', 'single', 'appears_on', 'compilation']
            artist = _find_artist_in_db_data(db_data, user_artist['id'])
            for composition in composition_types:
                compos = get_compositions(token, album_group=composition, limit=1, artist_id=user_artist['id'])
                if _compare_two_compositions(artist['latest_' + composition], compos):
                    # new composition
                    pass


conf = get_conf()
if __name__ == '__main__':
    my_username = "pva55ddk3p2lm234s5yhh2dyl"
    my_artists = initialization(my_username)

    db_dump(my_artists, 'initialize.json')
    _dump_artist_user(my_artists['artists'], my_username)

    check_updates()
    print('ЧЕКАЙ ЕБАЛО!')
