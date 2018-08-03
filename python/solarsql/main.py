#!/usr/bin/env python3
import threading
import time
import queue
import sys

import collector
import recorderdb
import uploader


class Bus(object):
    def __init__(self):
        self.event = queue.Queue()
        self.measure = queue.Queue()
        self.illu = queue.Queue()
        self.temp = queue.Queue()

def main():

    abus = Bus()
    bbus = Bus()
    cbus = Bus()

    ct = collector.Collector(abus)
    rt = recorderdb.RecorderDB(abus, bbus, cbus)
    ut = uploader.Uploader(bbus, cbus)

    ct.start()
    rt.start()
    ut.start()

    ct.join()
    rt.join()
    ut.join()


if __name__ == '__main__':
    main()


