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

        return self.get_albums(limit=1), self.get_singles_or_eps(limit=1), \
               self.get_appears_on(limit=1), self.get_compilations(limit=1)

    def get_albums(self, limit=None):
        """
        Получение всех альбомов артиста

        :params
            limit: количество альбомов для возврата (None - все)
        :return:
            Список альбомов
        """

        albums = self.connector.artist_albums(self.artist_id, album_type='album', limit=limit)
        artist_albums = albums_list_from_json(albums['items'])
        if limit is None:
            limit = albums['total']
        while albums['next']:
            if len(artist_albums) < limit:
                albums = self.connector.next(albums)
                artist_albums.append(albums['items'])
            elif len(artist_albums) >= limit:
                return artist_albums[:limit]

        return artist_albums

    def get_singles_or_eps(self, limit=None):
        """
        Получение всех синглов или EP артиста

        :params
            limit: количество альбомов для возврата (None - все)
        :return:
            Список синглов или EP
        """
        singles_eps = self.connector.artist_albums(self.artist_id, album_type='single')
        artist_singles = albums_list_from_json(singles_eps['items'])
        if limit is None:
            limit = singles_eps['total']
        while singles_eps['next']:
            if len(artist_singles) < limit:
                singles_eps = self.connector.next(singles_eps)
                artist_singles.append(singles_eps['items'])
            elif len(artist_singles) >= limit:
                return artist_singles[:limit]

        return artist_singles

    def get_appears_on(self, limit=None):
        """
        Получение всех произведений, где упомянается артист

        :params
            limit: количество альбомов для возврата (None - все)
        :return:
            Список произведений
        """
        appears = self.connector.artist_albums(self.artist_id, album_type='appears_on')
        artist_appears = albums_list_from_json(appears['items'])
        if limit is None:
            limit = appears['total']
        while appears['next']:
            if len(artist_appears) < limit:
                appears = self.connector.next(appears)
                artist_appears.append(appears['items'])
            elif len(artist_appears) >= limit:
                return artist_appears[:limit]

        return artist_appears

    def get_compilations(self, limit=None):
        """
        Получение всех подборок с артистом

        :params
            limit: количество альбомов для возврата (None - все)
        :return:
            Список подборок
        """
        compilations = self.connector.artist_albums(self.artist_id, album_type='compilation')
        artist_compilations = albums_list_from_json(compilations['items'])
        if limit is None:
            limit = compilations['total']
        while compilations['next']:
            if len(artist_compilations) < limit:
                compilations = self.connector.next(compilations)
                artist_compilations.append(compilations['items'])
            elif len(artist_compilations) >= limit:
                return artist_compilations[:limit]

        return artist_compilations


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
    return [artist_from_json(part, spotify) for part in js]


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
    return [album_from_json(part) for part in js]


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

art_list = artists_list_from_json(result['artists']['items'], sp)

# TEST
# result = sp.artist_albums(art_list[0].artist_id, limit=50)
# print(json.dumps(result, indent=4))

print(len(art_list[0].get_albums(sp)))
print(len(art_list[0].get_singles_or_eps(sp)))
print(len(art_list[0].get_appears_on(sp)))
print(len(art_list[0].get_compilations(sp)))
pass






"""
print(json.dumps(result, indent=4))
artists = result['artists']['items']
while result['artists']['next']:
    result = sp.next(result['artists'])
    artists.extend(result['artists']['items'])
"""




# Get artist albums
"""
artist_albums = {}  # artist_id: albums_list
for artist in artists:
    result = sp.artist(artist['id'])
    result = sp.artist_albums(artist['id'], limit=50)
    print(json.dumps(result, indent=4))
    artist_albums[artist['id']] = result['items']
    tt = Album.album_from_json(result['items'][0])
    print(tt.name)
    while result['next']:
        result = sp.next(result)
        artist_albums[artist['id']].append(result['items'])
    pprint.pprint(artist_albums[artist['id']])
    pass
pprint.pprint(artist_albums)
"""



# result = sp.current_user_followed_artists(after=None)
# result = sp.artist_albums('6zNJCgmbt1BbC9d9HWPaHx')  # Egor Nuts
# print(json.dumps(result, indent=4))

# result = sp.album_tracks('2DRxLSdoLRmAOMMbe4UymY')
# print(json.dumps(result, indent=4))

# result = sp.artist_albums('718COspgdWOnwOFpJHRZHS')
# print(json.dumps(result, indent=4))
