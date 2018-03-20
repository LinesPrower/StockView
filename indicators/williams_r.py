'''
Created on Mar 20, 2018

@author: LinesPrower
'''
from PyQt4 import QtGui
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator,\
    kTypeColor, windowAverage, windowFold

@addIndicator
class WilliamsR(Indicator):
    
    name = 'Williams %R'
    
    def __init__(self):
        Indicator.__init__(self)
        self.n = 7
        self.low = -80
        self.high = -20
        self.addParam('n', 'Число периодов', kTypeInt, 1, 1000)
        self.addParam('low', 'Нижняя граница', kTypeFloat, -100, 100)
        self.addParam('high', 'Верхняя граница', kTypeFloat, -100, 100, 
                      validator=lambda x: 'Верхняя граница должна быть больше нижней' if x <= self.low else None)    
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(self.low, 'red'), (self.high, 'green')]
        
        closing = [e.close for e in data]
        Hn = windowFold(closing, self.n, max, 0, 0)
        Ln = windowFold(closing, self.n, min, 1e10, 0)
        
        for i in range(len(data)):
            if Hn[i] == None:
                t = None
            else:
                t = (Hn[i] - closing[i]) / (Hn[i] - Ln[i]) * -100
            self.values.append(t)
            
        last_signal = None
        for i, x in enumerate(self.values):
            if x == None:
                continue
            sig = None
            if x < self.low:
                sig = False
            elif x > self.high:
                sig = True
            if sig != None and sig != last_signal:
                self.signals.append((i, sig))
                last_signal = sig            
            
        self.ready = True
        
        
    
def main():
    pass

if __name__ == '__main__':
    main()