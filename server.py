import time
import logging
import Resources.lostfilm as lf
import platform

logger = logging.getLogger("Core")
logger.setLevel(logging.DEBUG)
logfile = 'D:/Projects/Anaconda/DontMiss/Server/Logs/server.log' if platform.system() == 'Windows' else '/server.log'
fh = logging.FileHandler(logfile)
formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

sleep_time = 300


if __name__ == "__main__":
    start_time = time.time()
    lostfilm_initial_value = lf.LostFilm()
    logger.info("LostFilm initialization: %s seconds" % (time.time() - start_time))

    while True:
        try:
            lf_updates = lostfilm_initial_value.check_updates()
            if lf_updates:
                lf.send_notification(lf_updates)
            else:
                logger.info('No updates...')
            logger.info("Time to sleep....")
            time.sleep(sleep_time)
        except Exception as e:
            logger.error("Error in main loop: %s" % e)
    pass
