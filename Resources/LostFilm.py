from bs4 import BeautifulStoneSoup
import urllib.request as req
import logging

# TODO: Добавить try - except
# TODO: Переделать класс LostFilm

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

    def __init__(self, title="", description='//"', pub_date="", link=""):
        self.title = title  # Название сериала. Название серии (SnnEnn)
        self.description = description.split('//')[1].split('"')[0]  # Ссылка на лого сериала
        self.pubDate = pub_date  # Дата выхода
        self.link = link    # на страницу сериала

    def __eq__(self, other):
        return self.title == other.title


# Инициализация модуля
def initialization():
    xml_file = get_xml(LostFilm.URL)
    if xml_file:
        series = get_series_list(xml_file)
        return series[2]


# Получение xml-файла по ссылке
def get_xml(url):
    try:
        # Получение xml в string формате
        soup = BeautifulStoneSoup(req.urlopen(url).read())
        return soup
    except Exception as e:
        logger.error(log_message("Cannot get a XML-file: %s" % url, e))


# Получение списка серий из xml-файла
def get_series_list(soup):
    res = []
    try:
        # Формирование списка элементов в которых хранится информация о вышедших сериях
        items_list = soup.findAll('item')
        for item in items_list:
            title = item.find('title').text
            description = item.find('description').text
            pub_date = item.find('pubDate').text
            link = item.find('link').text

            series = LostFilm(title, description, pub_date, link)
            res.append(series)
        return res
    except Exception as e:
        logger.error(log_message("Cannot parse a xml-file. Please check xml-file", e))


# Поиск индекса последнего элемента в списке новых
def get_index(list_items, elem):
    for i in range(len(list_items)):
        if list_items[i] == elem:
            return i
    return -1
    pass


# Проверка обновлений
def check_updates(last_elem):
    updates = []
    logger.info("Start checking updates")
    xml_file = get_xml(LostFilm.URL)
    if xml_file:
        series = get_series_list(xml_file)
        if series:
            index = get_index(series, last_elem)
            for i in range(index):
                updates.append(series[i])
            updates.reverse()
            return updates


def log_message(msg, e):
    message = u"\t%s\n\tResource: %s \n\tERROR: %s. \n\t" % (msg, LostFilm.RESOURCE, e)
    return message
