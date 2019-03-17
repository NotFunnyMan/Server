import requests
import logging
import json
import platform

logger = logging.getLogger("Notify")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('D:/Projects/Anaconda/DontMiss/Server/Logs/server.log') if platform.system() == 'Windows' else '/server.log'
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_conf():
    logger.info('Reading a json configuration file...')
    try:
        file_path = 'Confs/notifysender_conf.json' if platform.system() == 'Windows' else 'Confs/notifysender_conf.json'
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        logger.exception('Cannot read json config!\n%s' % e)


conf = get_conf()
header = {'Content-Type': 'application/json',
          'Authorization': 'key=%s' % conf['APP_KEY']}


def send(updates):
    try:
        for update in updates:
            update['to'] = conf['MY_PHONE']
            logger.info("Send notification for resource: %s ; series: %s" % ('1', '2'))
            res = requests.post(conf['GOOGLE_URL'], headers=header, json=update)
            logger.debug("Notification status code: %s" % res.status_code)
            if res.status_code is not requests.codes.ok:
                logger.error("%s" % res.reason)
    except Exception as e:
        logger.exception("Cannot send data to google: %s" % e)
