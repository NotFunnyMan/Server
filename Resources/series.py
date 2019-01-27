import logging

logger = logging.getLogger("Series")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("/root/Server/server.log")
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


class Series(object):
    """
    Класс описывает параметры серии какого-либо сериала
    title - название сериала
    logo - ссылка на лого сериала
    pub_date - дата выхода серии
    link - ссылка на страницу сериала
    """

    def __init__(self, title="", description='//"', pub_date="", link=""):
        self.title = title  # Название сериала. Название серии (SnnEnn)
        self.logo = description.split('//')[1].split('"')[0]  # Ссылка на лого сериала
        self.pub_date = pub_date  # Дата выхода
        self.link = link    # на страницу сериала

    def __eq__(self, other):
        return self.title == other.title and self.pub_date == other.pub_date


def series_from_xml(xml, tag='item'):
    series_list = []
    try:
        items_list = xml.findAll(tag)
        for item in items_list:
            title = item.find('title').text
            description = item.find('description').text
            pub_date = item.find('pubDate').text
            link = item.find('link').text
            series_list.append(Series(title, description, pub_date, link))
        return series_list
    except Exception as e:
        logger.error("Cannot parse a xml-file. Please check xml-file: %s" % e)
        return Series()
