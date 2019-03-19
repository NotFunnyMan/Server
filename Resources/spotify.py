import spotipy
import spotipy.util as util
from spotipy.client import SpotifyException
import os
import time
import json
import logging
import platform

logger = logging.getLogger("Spotify")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("../Logs/spotify.log") if platform.system() == 'Windows' else logging.FileHandler("Logs/spotify.log")
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


class Artist(object):
    def __init__(self, artist_id, artist_uri, followers_total, name, genre, url, images):
        self.artist_id = artist_id
        self.artist_uri = artist_uri
        self.followers_total = followers_total
        self.name = name
        self.genre = genre
        self.url = url
        self.images = images
        self.latest_album, self.latest_single, self.latest_appears, self.latest_compilation = None, None, None, None

    def __eq__(self, other):
        return self.artist_id == other.artist_id


class Album(object):
    def __init__(self, album_id, album_uri, album_type, name, total_tracks, release_date, link, images):
        self.album_id = album_id
        self.album_uri = album_uri
        self.album_type = album_type
        self.name = name
        self.total_tracks = total_tracks
        self.release_date = release_date
        self.link = link
        self.images = images

    def __eq__(self, other):
        return self.album_id == other.album_id


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        logger.info("%s. Time spent: %s" % (func.__name__, time.time() - start))
        return res
    return wrapper


@benchmark
def get_conf():
    logger.info('Reading a json configuration file...')
    try:
        file_path = '../Confs/spotify_conf.json' if platform.system() == 'Windows' else 'Confs/spotify_conf.json'
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        logger.exception('Cannot read json config!\n%s' % e)


class User(object):

    def __init__(self, username):
        self.username = username
        self.token = spotipy.Spotify(auth=self.get_token())
        self.artists = self._filling_artists_with_albums(self.get_following_artists())

    @benchmark
    def get_token(self):
        logger.info('Creating a token...')
        try:
            token = util.prompt_for_user_token(self.username,
                                               scope=conf['SPOTIPY_SCOPE'],
                                               client_id=conf['SPOTIPY_CLIENT_ID'],
                                               client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                               redirect_uri=conf['SPOTIPY_REDIRECT_URI'],
                                               cache_path=conf['CACHE_PATH'] + ".cache-" + self.username)
        except Exception as e:
            logger.exception('Cannot get a token! Trying to remove cache-file and try again!')
            os.remove(f"{conf['CACHE_PATH']} + .cache-{self.username}")
            token = util.prompt_for_user_token(self.username,
                                               scope=conf['SPOTIPY_SCOPE'],
                                               client_id=conf['SPOTIPY_CLIENT_ID'],
                                               client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                               redirect_uri=conf['SPOTIPY_REDIRECT_URI'],
                                               cache_path=conf['CACHE_PATH'] + ".cache-" + self.username)
        return token

    def _artist_from_json(self, js):
        return Artist(js['id'], js['uri'], js['followers']['total'],
                      js['name'], js['genres'], js['external_urls']['spotify'], js['images'])

    def _artists_list_from_json(self, js):
        return [self._artist_from_json(part) for part in js]

    def _album_from_json(self, js):
        return Album(js['id'], js['uri'], js['album_type'], js['name'], js['total_tracks'], js['release_date'],
                     js['external_urls']['spotify'], js['images'])

    def _albums_list_from_json(self, js):
        return [self._album_from_json(part) for part in js]

    @benchmark
    def get_following_artists(self):
        logger.info('Getting follow artists...')
        try:
            result = self.token.current_user_followed_artists()
            art_list = self._artists_list_from_json(result['artists']['items'])
            while result['artists']['next']:
                result = self.token.next(result['artists'])
                art_list.extend(self._artists_list_from_json(result['artists']['items']))
            return art_list
        except SpotifyException as e:
            logger.exception("I caught the HTTPError\n%s" % e)
            if e.http_status == 401:
                logger.debug("Token was expired... Attempt to refresh the token and retry action")
                self.token = spotipy.Spotify(auth=self.get_token())
                self.get_following_artists()
        except Exception as e:
            logger.exception('Cannot get following artists!\n%s' % e)

    @benchmark
    def _filling_artists_with_albums(self, artists):
        for artist in artists:
            album, single, appears, compilation = self.get_latest_compositions(artist)
            artist.latest_album = album
            artist.latest_single = single
            artist.latest_appears = appears
            artist.latest_compilation = compilation
        return  artists

    def get_latest_compositions(self, artist):
        logger.info('Getting a latest compositions for artist: %s...' % artist.name)
        res = []
        composition_types = ['album', 'single', 'appears_on', 'compilation']
        for composition in composition_types:
            compos = self.get_compositions(album_group=composition, limit=1, artist=artist)
            res.append(compos if len(compos) != 0 else [None])
        return res[0][0], res[1][0], res[2][0], res[3][0]

    def get_compositions(self, album_group, artist, limit=None):
        logger.info('Getting %s "%s"' % (str(limit) if limit is not None else 'all',  album_group))
        artist_compositions = []
        try:
            compositions = self.token.artist_albums(artist.artist_id, album_type=album_group)
            artist_compositions.extend(self._albums_list_from_json(compositions['items']))
            if limit is None:
                limit = compositions['total']
            while compositions['next']:
                if len(artist_compositions) < limit:
                    compositions = self.token.next(compositions)
                    artist_compositions.append(compositions['items'])
                else:
                    break
            return artist_compositions[:limit]
        except SpotifyException as e:
            logger.exception("I caught the HTTPError\n%s" % e)
            if e.http_status == 401:
                logger.debug("Token was expired... Attempt to refresh the token and retry action")
                pass
        except Exception as e:
            logger.error('Cannot get the %s!\n%s' % (album_group, e))
            logger.exception('Cannot get the %s!')

    @staticmethod
    def _get_updates(new_artist, album_group, init_composition):
        updates = []
        last_ten_compositions = new_artist.get_compositions(limit=10, album_group=album_group)
        if album_group == 'album':
            logger.info('New album!')
            updates = last_ten_compositions[:last_ten_compositions.index(init_composition)]
        elif album_group == 'single':
            logger.info('New single or EP!')
            updates = last_ten_compositions[:last_ten_compositions.index(init_composition)]
        elif album_group == 'appears_on':
            logger.info('New appearance!')
            updates = last_ten_compositions[:last_ten_compositions.index(init_composition)]
        elif album_group == 'compilation':
            logger.info('New compilation!')
            updates = last_ten_compositions[:last_ten_compositions.index(init_composition)]

        logger.info('Artist:%s\nNew %s\n' % (new_artist.name, album_group))
        for update in updates:
            logger.info('Name: %s' % update.name)
        return updates

    @benchmark
    def check_updates(self, init_art_list):
        updates = []
        logger.info('Checking any updates...')
        try:
            current_artists_list = self.get_following_artists()
            for artist in current_artists_list:
                if artist in init_art_list:
                    init_artist = init_art_list[init_art_list.index(artist)]
                    if artist.latest_album != init_artist.latest_album:
                        updates = self._get_updates(artist, 'album', init_artist.latest_album)

                    if artist.latest_single != init_artist.latest_single:
                        updates = self._get_updates(artist, 'single', init_artist.latest_single)

                    if artist.latest_appears != init_artist.latest_appears:
                        updates = self._get_updates(artist, 'appears_on', init_artist.latest_appears)

                    if artist.latest_compilation != init_artist.latest_compilation:
                        updates = self._get_updates(artist, 'compilation', init_artist.latest_compilation)

            return updates, current_artists_list
        except SpotifyException as e:
            logger.exception("I caught the HTTPError\n%s" % e)
            if e.http_status == 401:
                logger.debug("Token was expired... Attempt to refresh the token and retry action")
                self.token = spotipy.Spotify(auth=self.get_token())
                updates, current_artists_list = self.check_updates(init_art_list)
                return updates, current_artists_list
        except Exception as e:
            logger.exception('Cannot get following artists!\n%s' % e)
            return [], init_art_list


# Get config
conf = get_conf()


def main():
    username = "pva55ddk3p2lm234s5yhh2dyl"
    logger.info('Spotify process was started...')
    me = User(username)
    init_artists_list = me.get_following_artists()

    while True:
        try:
            logger.info('Sleep DELAY_BTW_GET_UPDATES...')
            time.sleep(conf['DELAY_BTW_GET_UPDATES'])
            updates, init_artists_list = me.check_updates(init_artists_list)
            if updates:
                logger.info('We got any updates!')
        except Exception as e:
            logger.exception('Exception in main loop!\n%s' % e)


if __name__ == '__main__':
    main()
