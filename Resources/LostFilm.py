import xml.etree.ElementTree as Xml
import urllib.request as req
import logging as log


log.basicConfig(level=log.DEBUG, filename='server.log',
                format=u"%(filename)s\t[LINE:%(lineno)d]#\t %(levelname)-8s\t[%(asctime)s]\t%(message)s")


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
        root = Xml.ElementTree(req.urlopen(url).read()).getroot()
    except Exception as e:
        log.error(log_message("Cannot get a XML-file: %s" % url, e))
    else:
        # Создание xml из string
        root = Xml.fromstring(root)
        return root


# Получение списка серий из xml-файла
def get_series_list(root):
    res = []
    try:
        # Формирование списка элементов в которых хранится информация о вышедших сериях
        items = root[0].findall('item')
        for item in items:
            title = item.find('title').text
            description = item.find('description').text
            pub_date = item.find('pubDate').text
            link = item.find('link').text

            seria = LostFilm(title, description, pub_date, link)
            res.append(seria)
        return res
    except Exception as e:
        log.error(log_message("Cannot parse a xml-file. Please check xml-file", e))


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
