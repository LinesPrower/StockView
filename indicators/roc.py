'''
Created on Mar 15, 2018

@author: LinesPrower
'''
from PyQt4 import QtGui
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator

@addIndicator
class ROC(Indicator):
    
    name = 'ROC'
    
    def __init__(self, n=20):
        Indicator.__init__(self)
        self.n = n
        self.low = -1
        self.high = 1
        
        self.addParam('low', 'Нижняя граница', kTypeFloat, -100, 100)
        self.addParam('high', 'Верхняя граница', kTypeFloat, -100, 100, 
                      validator=lambda x: 'Верхняя граница должна быть больше нижней' if x <= self.low else None)
        self.addParam('n', 'n', kTypeInt, 1, 1000)
        
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(self.low, 'red'), (self.high, 'green'), (0, 'white')]
        last_signal = None
        for i in range(len(data)):
            if i < self.n:
                x = None
            else:
                x = 100 * (data[i].close - data[i-self.n].close) / data[i-self.n].close
                sig = None
                if x < self.low:
                    sig = True
                elif x > self.high:
                    sig = False
                if sig != None and sig != last_signal:
                    self.signals.append((i, sig))
                    last_signal = sig
            self.values.append(x)
        self.ready = True
        
    
def main():
    _ = QtGui.QApplication([])
    t = ROC()
    t.configure()
    print(t.getParams())

if __name__ == '__main__':
    main()