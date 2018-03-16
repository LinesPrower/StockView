'''
Created on Mar 15, 2018

@author: LinesPrower
'''
from PyQt4 import QtGui
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator,\
    kTypeColor, windowAverage

@addIndicator
class EMV(Indicator):
    
    name = 'EMV'
    
    def __init__(self):
        Indicator.__init__(self)
        self.n = 10
        self.addParam('n', 'Ширина окна сглаживания', kTypeInt, 1, 1000)    
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(0, 'pink')]
        for i in range(len(data)):
            if i < 1:
                x = None
            else:
                mm = (data[i].high - data[i].low) / 2 - (data[i-1].high - data[i].low) / 2
                br = data[i].vol / 10000 / (data[i].high - data[i].low)
                x = mm / br
            self.values.append(x)
            
        self.values = windowAverage(self.values, self.n)
        
        last_signal = None
        for i, x in enumerate(self.values):
            if x == None:
                continue
            sig = None
            if x > 0:
                sig = True
            elif x < 0:
                sig = False
            if sig != None and sig != last_signal:
                self.signals.append((i, sig))
                last_signal = sig            
            
        self.ready = True
        
        
    
def main():
    pass

if __name__ == '__main__':
    main()