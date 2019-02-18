import spotipy
import spotipy.util as util
import os
import time
import json
import logging

logger = logging.getLogger("Spotify")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("spotify.log")
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


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
            res.append(self.get_compositions(album_group=composition, limit=1)[0])
        return res[0], res[1], res[2], res[3]

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
            artist_compositions.append(albums_list_from_json(compositions['items']))
            while compositions['next']:
                if len(artist_compositions) < limit:
                    compositions = self.connector.next(compositions)
                    artist_compositions.append(compositions['items'])
                elif len(artist_compositions) >= limit:
                    return artist_compositions[:limit]
        except Exception as e:
            logger.error('Cannot get the %s!\n%s' % (album_group, e))
            return []
        return artist_compositions


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


def check_updates(init_art_list, curr_art_list, delay_api_request):
    updates = []
    logger.info('Checking any updates...')
    for artist in curr_art_list:
        if artist in init_art_list:
            album, single_ep, appears, compilation = artist.get_latest_compositions()
            init_artist = init_art_list[init_art_list.index(artist)]
            if album != init_artist.latest_album:
                logger.info('New album!')
                last_10_albums = artist.get_albums(limit=10)
                new_ones = last_10_albums[:last_10_albums.index(init_artist.latest_album)]
                updates.extend(new_ones)
                logger.info('Artist:%s\nNew albums\n' % artist.name)
                for ones in new_ones:
                    logger.info('Name: %s' % ones.name)
                artist.latest_album = album
            if single_ep != init_artist.latest_single:
                logger.info('New sing or EP!')
                last_10_single = artist.get_singles_or_eps(limit=10)
                new_ones = last_10_single[:last_10_single.index(init_artist.latest_single)]
                updates.extend(new_ones)
                logger.info('Artist:%s\nNew single or EP\n' % artist.name)
                for ones in new_ones:
                    logger.info('Name: %s' % ones.name)
                artist.latest_single = single_ep
            if appears != init_artist.latest_appears:
                logger.info('New appears!\n')
                last_10_appears = artist.get_albums(limit=10)
                new_ones = last_10_appears[:last_10_appears.index(init_artist.latest_appears)]
                updates.extend(new_ones)
                logger.info('Artist:%s\nNew appears\n' % artist.name)
                for ones in new_ones:
                    logger.info('Name: %s' % ones.name)
                artist.latest_appears = appears
            if compilation != init_artist.latest_compilation:
                logger.info('New compilation!\n')
                last_10_compilations = artist.get_compilations(limit=10)
                new_ones = last_10_compilations[:last_10_compilations.index(init_artist.latest_compilation)]
                updates.extend(new_ones)
                logger.info('Artist:%s\nNew albums\n' % artist.name)
                for ones in new_ones:
                    logger.info('Name: %s' % ones.name)
                artist.latest_compilation = compilation
            logger.info('Time to sleep....')
            time.sleep(delay_api_request)
    return updates


def get_token(conf):
    token = None
    logger.info('Creating a token...')
    try:
        token = util.prompt_for_user_token(conf['username'],
                                           scope=conf['SPOTIPY_SCOPE'],
                                           client_id=conf['SPOTIPY_CLIENT_ID'],
                                           client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=conf['SPOTIPY_REDIRECT_URI'])
    except Exception as e:
        logger.error('Cannot get a token! Trying to remove cache-file and try again!\n%s' % e)
        os.remove(f".cache-{conf['username']}")
        token = util.prompt_for_user_token(conf['username'],
                                           scope=conf['SPOTIPY_SCOPE'],
                                           client_id=conf['SPOTIPY_CLIENT_ID'],
                                           client_secret=conf['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=conf['SPOTIPY_REDIRECT_URI'])
    return token


def get_following_artists(spotify):
    logger.info('Getting follow artists...')
    try:
        result = spotify.current_user_followed_artists()
        art_list = artists_list_from_json(result['artists']['items'], spotify)
        while result['artists']['next']:
            result = spotify.next(result['artists'])
            art_list.extend(artists_list_from_json(result['artists']['items'], spotify))
        return art_list
    except Exception as e:
        logger.error('Cannot get following artists!\n%s' % e)
        return []


def get_artists_list(conf):
    token = get_token(conf)
    spotify = spotipy.Spotify(auth=token)
    return get_following_artists(spotify)


def get_conf():
    logger.info('Reading a json configuration file...')
    try:
        with open('../spotify_conf.json') as f:
            return json.load(f)
    except Exception as e:
        logger.error('Cannot read json config!\n%s' % e)
        return {}


def main():
    logger.info('Spotify process was started...')
    conf = get_conf()
    init_artists_list = get_artists_list(conf)

    while True:
        try:
            current_artists_list = get_artists_list(conf)
            updates = check_updates(init_artists_list, current_artists_list, conf['DELAY_API_REQUEST'])
            if updates:
                logger.info('We got any updates!')
            init_artists_list = current_artists_list
            logger.info('Sleep DELAY_BTW_GET_UPDATES...')
            time.sleep(conf['DELAY_BTW_GET_UPDATES'])
        except Exception as e:
            logger.error('Exception in main loop!\n%s' % e)


if __name__ == '__main__':
    # result = sp.current_user_followed_artists(after=None)
    # result = sp.artist_albums('6zNJCgmbt1BbC9d9HWPaHx')  # Egor Nuts
    # print(json.dumps(result, indent=4))
    main()


