import xml.etree.ElementTree as xml
import urllib.request as req
from bs4 import BeautifulSoup
import logging as log

RESOURCE = "NewStudio.tv"
URL = "http://newstudio.tv/rss.php"

log.basicConfig(level = log.DEBUG, filename = '../../server.log', format = u"%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")


class NewStudio(object):
    """Ресурс: NewStudio.tv
    Класс хранит информацию о RSS-ленте ресурса NewStudio.tv: http://newstudio.tv
    RSS-лента представлена в файле типа php, но в разметке xml: http://newstudio.tv/rss.php
    """


    def __init__(self, title = "", description = "", pubDate = "", link = ""):
        self.title = title.split("WEB")[0]  # Название сериала. Название серии (SnnEnn)
        self.description = description  # Ссылка на лого сериала
        self.pubDate = pubDate  # Дата выхода
        self.link = link    # Ссылка на страницу сериала

    def __eq__(self, other):
        return self.title == other.title


# Инициализация модуля
def Initialization():
    xml_file = GetXML(URL)
    if (xml_file):
        series = GetSeriesList(xml_file)
        if (series):
            return series[2]


# Получение xml-файла по ссылке
def GetXML(url):
    # Получение xml в string формате
    try:
        root = xml.ElementTree(req.urlopen(url).read()).getroot()
    except Exception as e:
        log.error(log_message("Cannot get a XML-file: %s" % url, e))
    else:
        # Создание xml из string
        root = xml.fromstring(root)
        return root


# Получение ссылки на иконку сериала
def GetSerialIcon(url):
    try:
        content = req.urlopen(url).read()
    except Exception as e:
        log.error(log_message("Cannot get an icon. url = %s" % url, e))
    else:
        soup = BeautifulSoup(content, "html.parser")
        film_list = soup.find('var', {'class': 'postImg'}).get("title")
        return film_list


# Получение списка серий из xml-файла
def GetSeriesList(root):
    res = []
    try:
        # Формирование списка элементов в которых хранится информация о вышедших сериях
        items = root[0].findall('item')
        for item in items:
            title = item.find('title').text
            pubDate = item.find('pubDate').text
            link = item.find('link').text
            description = ""

            seria = NewStudio(title, description, pubDate, link)
            if (GetIndex(res, seria) == -1):
                res.append(seria)

        for r in res:
            icon = GetSerialIcon(r.link)
            if (icon):
                r.description = icon
            else:
                r.description = "NO ICON!"
        return res
    except Exception as e:
        log.error(log_message("Cannot parse a xml-file. Please check xml-file", e))


# Поиск индекса последнего элемента в списке новых
def GetIndex(list, elem):
    for i in range(len(list)):
        if list[i] == elem:
            return i
    return -1


# Проверка обновлений
def CheckUpdates(last_elem):
    updates = []
    xml_file = GetXML(URL)
    if (xml_file):
        series = GetSeriesList(xml_file)
        if (series):
            index = GetIndex(series, last_elem)
            for i in range(index):
                updates.append(series[i])
            updates.reverse()
            return updates


def log_message(msg, e):
    str = u"Resource: %s. \n\t ERROR: %s. \n\t ERROR MESSAGE: \n\t %s" % (RESOURCE, msg, e)
    return str