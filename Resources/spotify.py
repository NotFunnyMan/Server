import spotipy
import spotipy.util as util
import os
import time
import json
import logging
from spotipy.client import SpotifyException
import platform

logger = logging.getLogger("Spotify")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("../Logs/spotify.log")
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_conf():
    logger.info('Reading a json configuration file...')
    try:
        file_path = '../Confs/spotify_conf.json' if platform.system() == 'Windows' else 'spotify_conf.json'
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        logger.exception('Cannot read json config!\n%s' % e)


conf = get_conf()


class Artist(object):
    """
    Класс описывает объект Артист

    artist_id - id артиста
    uri - uri артиста
    followers_total - количество фолловеров
    name - имя артиста
    genre - список жанров артиста
    url - ссылка на профиль артиста
    images - список аватаров артиста разных размеров
    spotify - объект типа spotipy.Spotify

    latest_album - последний альбом
    latest_single - последний сингл или EP
    latest_appears - последняя композиция, где артист упоминается
    latest_compilation - последняя подборка
    """

    def __init__(self, artist_id, artist_uri, followers_total, name, genre, url, images, spotify):
        self.artist_id = artist_id
        self.artist_uri = artist_uri
        self.followers_total = followers_total
        self.name = name
        self.genre = genre
        self.url = url
        self.images = images
        self.connector = spotify
        self.latest_album, self.latest_single, self.latest_appears, self.latest_compilation = \
            self.get_latest_compositions()

    def __eq__(self, other):
        return self.artist_id == other.artist_id

    def get_latest_compositions(self):
        """
        Получение по последней композиции по каждой из категории:
        album - альбом
        single_ep - сингл или EP
        appears_on - совместный трек с другим артистом
        compilation - подборка из треков

        :return:
            Последний альбом по каждой из категории
        """
        logger.info('Getting a latest compositions for artist: %s...' % self.name)
        res = []
        composition_types = ['album', 'single', 'appears_on', 'compilation']
        for composition in composition_types:
            compos = self.get_compositions(album_group=composition, limit=1)
            res.append(compos if len(compos) != 0 else [None])
        return res[0][0], res[1][0], res[2][0], res[3][0]

    def get_compositions(self, album_group, limit=None):
        """
        Получение всех альбомов артиста

        :params
            album_group: один из типов: 'album', 'single', 'appears_on' или 'compilation'
            limit: количество композиций для возврата (None - все)
        :return:
            Удача: список композиций
            Ошибка: пустой список
        """

        logger.info('Getting %s "%s"' % (str(limit) if limit is not None else 'all',  album_group))
        artist_compositions = []
        try:
            compositions = self.connector.artist_albums(self.artist_id, album_type=album_group)
            artist_compositions.extend(albums_list_from_json(compositions['items']))
            if limit is None:
                limit = compositions['total']
            while compositions['next']:
                if len(artist_compositions) < limit:
                    compositions = self.connector.next(compositions)
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


def artist_from_json(js, spotify):
    """
    Создание класса Артист из фрагмента json

    :params
        js: json-фрагмент
        spotify: объект типа spotipy.Spotify
    :return
        класс Артист
    """
    return Artist(js['id'], js['uri'], js['followers']['total'],
                  js['name'], js['genres'], js['external_urls']['spotify'], js['images'], spotify)


def artists_list_from_json(js, spotify):
    """
    Создание списка объектов класса Артист из списка json
    :param
        js: json-объект
    :return:
        Список объектов Артист из списка json
    """
    return [artist_from_json(part, spotify) for part in js]


class Album(object):
    """
    Класс описывает объект Альбом

    album_id - id альбома
    album_uri - uri альбома
    album_type - тип альбома (album, single_ep, appears_on, compilation)
    name - название альбома
    total_tracks - количество треков в альбоме
    release_date - дата выхода
    link - ссылка на альбом
    images - список ссылок на обложки альбома разных размеров
    """

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

    @staticmethod
    def album_from_json(js):
        return Album(js['id'], js['uri'], js['album_type'], js['name'],
                     js['total_tracks'], js['release_date'], js['external_urls']['spotify'], js['images'])


def album_from_json(js):
    """
    Создание класса Альбом из фрагмента json

    :params
        js: json-фрагмент
    :return
        класс Альбом
    """
    return Album(js['id'], js['uri'], js['album_type'], js['name'], js['total_tracks'], js['release_date'],
                 js['external_urls']['spotify'], js['images'])


def albums_list_from_json(js):
    """
    Создание списка объектов класса Альбом из списка json
    :param
        js: json-объект
    :return:
        Список объектов Альбом из списка json
    """
    return [album_from_json(part) for part in js]


class User(object):
    """
    Класс описывает объект User

    username - имя пользователя
    token - токен для работы с пользователем
    """
    def __init__(self, username):
        self.username = username
        self.token = spotipy.Spotify(auth=self.get_token())

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

    def get_following_artists(self):
        logger.info('Getting follow artists...')
        try:
            result = self.token.current_user_followed_artists()
            art_list = artists_list_from_json(result['artists']['items'], self.token)
            while result['artists']['next']:
                result = self.token.next(result['artists'])
                art_list.extend(artists_list_from_json(result['artists']['items'], self.token))
            return art_list
        except SpotifyException as e:
            logger.exception("I caught the HTTPError\n%s" % e)
            if e.http_status == 401:
                logger.debug("Token was expired... Attempt to refresh the token and retry action")
                self.token = spotipy.Spotify(auth=self.get_token())
                self.get_following_artists()
        except Exception as e:
            logger.exception('Cannot get following artists!\n%s' % e)

    def check_updates(self, init_art_list):
        updates = []
        logger.info('Checking any updates...')
        try:
            current_artists_list = self.get_following_artists()
            for new_artist in current_artists_list:
                if new_artist in init_art_list:
                    init_artist = init_art_list[init_art_list.index(new_artist)]
                    if new_artist.latest_album != init_artist.latest_album:
                        logger.info('New album!')
                        last_10_albums = new_artist.get_compositions(limit=10, album_group='album')
                        new_ones = last_10_albums[:last_10_albums.index(new_artist.latest_album)]
                        updates.extend(new_ones)
                        logger.info('Artist:%s\nNew albums\n' % new_artist.name)
                        for ones in new_ones:
                            logger.info('Name: %s' % ones.name)

                    if new_artist.latest_single != init_artist.latest_single:
                        logger.info('New sing or EP!')
                        last_10_single = new_artist.get_compositions(limit=10, album_group='single')
                        new_ones = last_10_single[:last_10_single.index(new_artist.latest_single)]
                        updates.extend(new_ones)
                        logger.info('Artist:%s\nNew single or EP\n' % new_artist.name)
                        for ones in new_ones:
                            logger.info('Name: %s' % ones.name)

                    if new_artist.latest_appears != init_artist.latest_appears:
                        logger.info('New appears!\n')
                        last_10_appears = new_artist.get_compositions(limit=10, album_group='appears_on')
                        new_ones = last_10_appears[:last_10_appears.index(new_artist.latest_appears)]
                        updates.extend(new_ones)
                        logger.info('Artist:%s\nNew appears\n' % new_artist.name)
                        for ones in new_ones:
                            logger.info('Name: %s' % ones.name)

                    if new_artist.latest_compilation != init_artist.latest_compilation:
                        logger.info('New compilation!\n')
                        last_10_compilations = new_artist.get_compositions(limit=10, album_group='compilation')
                        new_ones = last_10_compilations[:last_10_compilations.index(new_artist.latest_compilation)]
                        updates.extend(new_ones)
                        logger.info('Artist:%s\nNew albums\n' % new_artist.name)
                        for ones in new_ones:
                            logger.info('Name: %s' % ones.name)
            return updates, current_artists_list
        except SpotifyException as e:
            logger.exception("I caught the HTTPError\n%s" % e)
            if e.http_status == 401:
                logger.debug("Token was expired... Attempt to refresh the token and retry action")
                self.token = spotipy.Spotify(auth=self.get_token())
        except Exception as e:
                logger.exception('Cannot get following artists!\n%s' % e)


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
    # result = sp.current_user_followed_artists(after=None)
    # result = sp.artist_albums('6zNJCgmbt1BbC9d9HWPaHx')  # Egor Nuts
    # print(json.dumps(result, indent=4))
    main()


