#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import threading
import random
import datetime

import crc
import memorymapping
import concatenate
import devices
from invertersimu import InverterSimulator

def dumphex(pkt):
    result = ' '.join(['{:02x}'.format(b) for b in pkt]) # debug
    return result


def response_modbus_packet(rxpacket, inverters):
    print('{:.3f}: {}'.format(time.time(), dumphex(rxpacket)))
    #print('[35;42m{:.3f}:[m {}'.format(time.time(), dumphex(rxpacket)))
    #print('[31m{:.3f}:[m {}'.format(time.time(), dumphex(rxpacket)))

    for inv in inverters:
        try:
            result = inv.read_memory_by_modbus(rxpacket)
            return result
        except ValueError as ex: 
            pass


if __name__ == '__main__':

    print('Modbus Slave Simulator')

    inverters = [InverterSimulator(id) for id in range(1,3)]
    [print(inv) for inv in inverters]

    modbuslistener = concatenate.ModbusListener(callback=response_modbus_packet, args=inverters)
    modbuslistener.start() 
    modbuslistener.join()








