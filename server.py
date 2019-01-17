import time
import logging

import NotifySender as Notify
import Resources.LostFilm as Lf


sleep_time = 300
lostfilm_initial_value = Lf.LostFilm()


def initialization():
    global lostfilm_initial_value
    start_time = time.time()
    lostfilm_initial_value = Lf.initialization()
    logger.info("LostFilm initialization: %s seconds" % (time.time() - start_time))


if __name__ == "__main__":
    logger = logging.getLogger("Core")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("server.log")
    formatter = logging.Formatter(u"%(asctime)s : %(levelname)-5s : %(filename)s : %(name)s logger : %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    initialization()
    while True:
        lf_updates = Lf.check_updates(lostfilm_initial_value)
        if lf_updates:
            Notify.send(lf_updates, Lf.LostFilm.RESOURCE)
            lostfilm_initial_value = lf_updates[-1]
        logger.info("Time to sleep....")
        time.sleep(sleep_time)
    pass
