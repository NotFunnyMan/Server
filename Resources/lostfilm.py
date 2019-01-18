import Resources.series as series
from bs4 import BeautifulStoneSoup
import urllib.request as req
import logging


logger = logging.getLogger("LostFilm")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("server.log")
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
            soup = BeautifulStoneSoup(req.urlopen(self.URL).read())
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
                updates = [elem for elem in series_list if elem not in self.FEED]  # self.FEED
                self.FEED = updates + self.FEED[:-len(updates)]
                updates.reverse()
                return updates
            else:
                return []
        except Exception as e:
            logger.error("Check failed : %s" % e)
            return []
