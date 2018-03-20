'''
Created on Mar 14, 2018

@author: LinesPrower
'''
import io
from math import ceil

kScaleHour = 0
kScaleDay  = 1

class DataEntry:
    def __init__(self, date, time, open, high, low, close, vol):
        self.date = int(date)
        self.time = int(time)
        self.open = float(open)
        self.close = float(close)
        self.low = float(low)
        self.high = float(high)
        self.vol = float(vol)

class EFileFormatError(Exception):
    def __init__(self, message):
        self.message = message

class StockData:
    def __init__(self):
        self.name = ''
        self.raw_data = []
        self.data = []
        self.scale = kScaleHour
        
    kFormatStr = '<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>'
        
    def load(self, fname):
        self.raw_data.clear()
        with io.open(fname, encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if i == 0:
                    if line != self.kFormatStr:
                        raise EFileFormatError('Invalid file format. Expected: %s' % self.kFormatStr)
                    continue
                t = line.split(',')
                if i == 1:
                    self.name = t[0]
                self.raw_data.append(DataEntry(*t[2:9]))
                
    def setScale(self, scale):
        self.data = makeScaled(self.raw_data, scale)
        self.scale = scale

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

def makeScaled(data, scale):
    res = []
    i = 0
    n = len(data)
    
    def eq(e1, e2):
        if scale == kScaleDay:
            return e1.date == e2.date
        if scale == kScaleHour:
            return e1.time // 10000 == e2.time // 10000
        return False
    
    while i < n:
        j = i
        while j < n and eq(data[j], data[i]):
            j += 1
        res.append(DataEntry(
            data[i].date,
            data[j-1].time,
            data[i].open,
            max(data[t].high for t in range(i, j)),
            min(data[t].low for t in range(i, j)),
            data[j-1].close,
            sum(data[t].vol for t in range(i, j))
            ))
        i = j
    return res
    
def main():
    print(getTicks(2790, 5326, 800))
    #test = StockData()
    #test.load(r'Finam_data\GAZP_170314_180314.txt')
    #print(len(test.data))
    

if __name__ == '__main__':
    main()