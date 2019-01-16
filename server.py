import time
import logging as log

import NotifySender as Notify
import Resources.LostFilm as Lf


sleep_time = 300
lostfilm_initial_value = Lf.LostFilm()


def initialization():
    global lostfilm_initial_value
    start_time = time.time()
    lostfilm_initial_value = Lf.Initialization()
    print("---LF: %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    log.basicConfig(level=log.ERROR, filename='../../server.log',
                    format=u"%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")

    initialization()
    while True:
        lf_updates = Lf.CheckUpdates(lostfilm_initial_value)
        if lf_updates:
            Notify.Send(lf_updates, Lf.LostFilm.RESOURCE)
            lostfilm_initial_value = lf_updates[-1]
        #time.sleep(sleep_time)
    pass
