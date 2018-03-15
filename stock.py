'''
Created on Mar 14, 2018

@author: LinesPrower
'''
import io
from math import ceil

class DataEntry:
    def __init__(self, date, time, open, high, low, close):
        self.date = int(date)
        self.time = int(time)
        self.open = float(open)
        self.close = float(close)
        self.low = float(low)
        self.high = float(high)

class EFileFormatError(Exception):
    def __init__(self, message):
        self.message = message

class StockData:
    def __init__(self):
        self.name = ''
        self.data = []
        
    kFormatStr = '<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>'
        
    def load(self, fname):
        self.data.clear()
        with io.open(fname, encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if i == 0:
                    if line != self.kFormatStr:
                        raise EFileFormatError('Invalid file format. Expected: %s' % self.kFormatStr)
                    continue
                t = line.split(',')[2:8]
                self.data.append(DataEntry(*t))

def getTickInterval(delta):
    best = 1
    for k in range(-20, 20):
        for mpl in [1, 0.5, 0.2]:
            x = pow(10.0, k) * mpl
            if abs(x - delta) < abs(best - delta):
                best = x
    return best

def getTicks(min_val, max_val, width, opt_dist = 30):
    opt_delta = (max_val - min_val) / (width / opt_dist)
    delta = getTickInterval(opt_delta)
    t = ceil(min_val / delta) * delta
    res = []
    while t <= max_val:
        res.append(t)
        t += delta
    return res
    
def main():
    print(getTicks(2790, 5326, 800))
    #test = StockData()
    #test.load(r'Finam_data\GAZP_170314_180314.txt')
    #print(len(test.data))
    

if __name__ == '__main__':
    main()