'''
Created on Mar 19, 2018

@author: LinesPrower
'''
from PyQt4 import QtGui
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator,\
    kTypeColor, windowAverage

@addIndicator
class MFI(Indicator):
    
    name = 'MFI'
    
    def __init__(self):
        Indicator.__init__(self)
        self.n = 14 * 8
        self.addParam('n', 'Число периодов', kTypeInt, 1, 1000)    
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(20, 'red'), (80, 'green')]
        mf = []
        positive = []
        last = 0 
        for e in data:
            t = (e.high + e.low + e.close) / 3 * e.vol
            positive.append(t > last)
            mf.append(t)
            last = t
        m = len(data)
        pmf = 0
        nmf = 0
        for i in range(m):
            if i >= self.n:
                if positive[i - self.n]:
                    pmf -= mf[i - self.n]
                else:
                    nmf -= mf[i - self.n]
                    
            if positive[i]:
                pmf += mf[i]
            else:
                nmf += mf[i]
            if i >= self.n - 1 and abs(nmf) > 1e-10:
                mr = pmf / nmf
                t = 100 - 100 / (1 + mr)
            else:
                t = None
            self.values.append(t)
            
        last_signal = None
        for i, x in enumerate(self.values):
            if x == None:
                continue
            sig = None
            if x < 20:
                sig = True
            elif x > 80:
                sig = False
            if sig != None and sig != last_signal:
                self.signals.append((i, sig))
                last_signal = sig            
            
        self.ready = True
        
        
    
def main():
    pass

if __name__ == '__main__':
    main()