import Resources.series as series
from bs4 import BeautifulStoneSoup
import urllib.request as req
import logging


logger = logging.getLogger("LostFilm")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("../Logs/server.log")
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
    FEED = []

    # Инициализация модуля
    def __init__(self):
        try:
            # Получение xml в string формате
            with req.urlopen(self.URL) as open_url:
                soup = BeautifulStoneSoup(open_url.read())
                self.FEED = (series.series_from_xml(soup, 'item'))[2:]
        except Exception as e:
            logger.error("Cannot get a XML-file: %s" % e)

    # Проверка обновлений
    def check_updates(self):
        logger.info("Start checking updates")
        try:
            xml_file = BeautifulStoneSoup(req.urlopen(self.URL).read())
            if xml_file:
                series_list = series.series_from_xml(xml_file)
                updates = [elem for elem in series_list if elem not in self.FEED]
                if len(self.FEED) == 12:
                    self.FEED = updates + self.FEED[:-len(updates)]
                else:
                    self.FEED = updates + self.FEED
                updates.reverse()
                return updates
            else:
                return []
        except Exception as e:
            logger.error("Check failed : %s" % e)
            return []
