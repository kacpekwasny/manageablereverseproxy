from multiprocessing import Manager, Process, Lock, Value, Array
from datetime import datetime
from random import random
from time import sleep


def request_maker(d: dict, l: Lock, i: int):
    for _ in range(100):
        l.acquire()
        try:
            print(i, 'is appending')
            d['ip'].append(datetime.now())
        finally:
            l.release()
        sleep(random()/100)


def request_meter(d: dict, l: Lock):
    while True:
        # l.acquire()
        rqs = d['ip'][:]
        ln = len(rqs)
        # print(ln)

        if ln > 2:
            t = rqs[-1] - rqs[0]
            print(ln, t, t/ln)
            if ln >= 1000:
                return
        # try:

        # finally:
            # l.release()


if __name__ == '__main__':
    # mp.set_start_method('spawn')
    l = Lock()
    m = Manager()
    d = m.dict()
    d['ip'] = m.list()

    p2 = Process(target=request_meter, args=(d,l))
    prms = [
        Process(target=request_maker, args=(d,l,i))
        for i in range(10)
    ]

    p2.start()
    for p in prms: p.start()

    p2.join()

    for p in prms: p.join()
    