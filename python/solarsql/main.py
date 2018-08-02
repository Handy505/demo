#!/usr/bin/env python3
import threading
import time
import queue
import sqlite3
import random
import queue
import sys

import recorderdb

class InverterRecord(object):
    def __init__(self, mid, timestamp, kw, kwh):
        self.mid = mid
        self.timestamp = timestamp
        self.kw = kw 
        self.kwh = kwh

    def __str__(self):
        ts = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(self.timestamp))
        return '{},{},{},{}'.format(self.mid, ts, self.kw, self.kwh)




class InverterMeasurement(object):
    pass

class InverterAlarmEvent(object):
    def __init__(self, mid, timestamp, older_code, newer_code):
        self.mid = mid
        self.timestamp = timestamp
        self.older_code = older_code 
        self.newer_code = newer_code 

    def __str__(self):
        ts = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(self.timestamp))
        return '{},{},{:>8},{:>8}'.format(self.mid, ts, bin(self.older_code), bin(self.newer_code))

    def infomations(self):
        results = []
        for shift in range(0, 8):
            mask = 0x01 << shift
            newerbit = self.newer_code & mask
            olderbit = self.older_code & mask
            if olderbit != newerbit:
                ts = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(self.timestamp))
                stat = 'H' if newerbit else 'R'
                s = '{},{},1,{},{}'.format(self.mid, ts, shift, stat)
                results.append(s)
        return results







class InverterErrorEvent(object):
    pass
class InverterOnlineEvent(object):
    pass
class InverterOfflineEvent(object):
    pass




class PVInverter(object):
    def __init__(self, mid):
        self.mid = mid
        self.alarm_code = 0
        self.error_code = 0
        self.events = []
        self.kw = 0
        self.kwh = 1000
       
    def __str__(self):
        #return 'Inverter-{}, {:>5.3f} kw, {:>7.3f} kwh'.format(self.mid, round(self.kw,3), round(self.kwh,3))
        return 'Inverter-{}, {:>5.3f} kw, {:>7.3f} kwh, {} events'.format(
            self.mid, round(self.kw,3), round(self.kwh,3), len(self.events))

    def sync_with_hardware(self):
        time.sleep(random.randint(50,200)/1000)

        # event
        current_code = random.randint(0,16)
        if current_code != self.alarm_code:
            aevent = InverterAlarmEvent(self.mid, time.time(), self.alarm_code, current_code)
            self.events.append(aevent)
            self.alarm_code = current_code
                
        # measurement
        self.kw = (random.randint(0,1000)/1000)
        self.kwh += self.kw

    def make_record(self):
        return InverterRecord(self.mid, time.time(), round(self.kw,3), round(self.kwh,0))



class Collector(threading.Thread):
    def __init__(self, obus):
        threading.Thread.__init__(self)       
        self.obus = obus


    def run(self):
    
        pvgroup = [PVInverter(i) for i in range(1,3)]
        [print(pv) for pv in pvgroup]


        ltime = time.localtime()
        while True:

            [pv.sync_with_hardware() for pv in pvgroup]
            
            #[print(pv) for pv in pvgroup]


            if time.localtime().tm_min != ltime.tm_min:
                print('New minute: {}'.format(ltime.tm_min))

                for pv in pvgroup:
                    print(pv)
                    [self.obus.event.put(e) for e in pv.events]
                    pv.events.clear()


                for pv in pvgroup:
                    r = pv.make_record()
                    print('Get new records: {}'.format(r))
                    self.obus.measure.put(r)


                ltime = time.localtime()

            time.sleep(1)


class Uploader(threading.Thread):
    def __init__(self, ibus, obus):
        threading.Thread.__init__(self)       
        self.ibus = ibus 
        self.obus = obus 

    def run(self):
        while True:
            #print('U: {}'.format(time.time()))
            time.sleep(1)


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



    aqueue = queue.Queue()
    bqueue = queue.Queue()
    cqueue = queue.Queue()

    '''ct = Collector(aqueue)
    rt = recorderdb.RecorderDB(aqueue, bqueue, cqueue)
    ut = Uploader(bqueue, cqueue)
    '''

    ct = Collector(abus)
    rt = recorderdb.RecorderDB(abus, bbus, cbus)
    ut = Uploader(bbus, cbus)

    ct.start()
    rt.start()
    ut.start()

    ct.join()
    rt.join()
    ut.join()


if __name__ == '__main__':
    main()

    '''pv = PVInverter(1)
    [pv.sync_with_hardware() for _ in range(10)]

    for e in pv.events:
        print(e)
        eventstrings = e.infomations()
        [print('\t{}'.format(s)) for s in eventstrings]
        '''
            




