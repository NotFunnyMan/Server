import xmltodict
import urllib.request as req
import logging
import NotifySender as ns
import random
import platform

logger = logging.getLogger("LostFilm")
logger.setLevel(logging.DEBUG)


logfile = 'D:/Projects/Anaconda/DontMiss/Server/Logs/server.log' if platform.system() == 'Windows' else '/server.log'
fh = logging.FileHandler(logfile)
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


class LostFilm(object):
    """Ресурс: LostFilm.tv
    Класс хранит информацию о RSS-ленте ресурса LostFilm.tv: http://www.lostfilm.tv/
    RSS-лента в формате xml: http://www.lostfilm.tv/rss.xml
    """

    RESOURCE = "LostFilm.tv"
    URL = "http://www.lostfilm.tv/rss.xml"

    def __init__(self):
        try:
            feed = self.get_rss_feed()
            self.series_list = feed['rss']['channel']['item']
        except Exception as e:
            logger.exception("Cannot get a RSS-feed: %s" % e)

    def check_updates(self):
        logger.info("Start checking updates")
        try:
            new_feed = self.get_rss_feed()
            if new_feed:
                new_series_list = new_feed['rss']['channel']['item']
                updates = self._series_comparison(self.series_list[2:], new_series_list)  # "2:" для теста
                self.series_list = new_series_list
                return updates
            else:
                return []
        except Exception as e:
            logger.exception("Check failed: %s" % e)
            return []

    def get_rss_feed(self):
        feed = self._read_xml()
        return self._xml_to_json(feed.decode('utf-8').replace('&', 'and'))

    def _read_xml(self):
        with req.urlopen(self.URL) as open_url:
            return open_url.read()

    @staticmethod
    def _xml_to_json(xml):
        return xmltodict.parse(xml, encoding='utf-8')

    @staticmethod
    def _series_comparison(old_data, new_data):
        updates = []
        for new in new_data:
            if new not in old_data:
                updates.append(new)
        return updates


def send_notification(updates):
    result = []
    for update in updates:
        logger.info("New series: %s ; series: %s" % (LostFilm.RESOURCE, update['title']))
        data = {
            "data":
                {
                    "body": update['title'],
                    "title": "Вышла новая серия сериала на " + LostFilm.RESOURCE,
                    "icon": "http:" + update['description'].split('"')[1],
                    "resource": LostFilm.RESOURCE,
                    "sound": "default",
                    "priority": "high",
                    "id": random.randint(1, 1000)
                },
            }
        result.append(data)
    result.reverse()
    ns.send(result)
