import time
import logging

import NotifySender as Notify
import Resources.lostfilm as lf

logger = logging.getLogger("Core")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("server.log")
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


sleep_time = 5
start_time = time.time()
lostfilm_initial_value = lf.LostFilm()
logger.info("LostFilm initialization: %s seconds" % (time.time() - start_time))


if __name__ == "__main__":
    while True:
        try:
            lf_updates = lostfilm_initial_value.check_updates()
            if lf_updates:
                Notify.send(lf_updates, lostfilm_initial_value.RESOURCE)
            else:
                logger.info('No updates...')
            logger.info("Time to sleep....")
            time.sleep(sleep_time)
        except Exception as e:
            logger.error("Error in main loop: %s" % e)
    pass
