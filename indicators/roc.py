#===============================================================================
# StockView
# Copyright (C) 2018 Damir Akhmetzyanov
# 
# This file is part of StockView
# 
# StockView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# StockView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================
from PyQt4 import QtGui
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator,\
    kTypeColor

@addIndicator
class ROC(Indicator):
    
    name = 'ROC'
    
    def __init__(self):
        Indicator.__init__(self)
        self.n = 20
        self.low = -1
        self.high = 1
        self.low_color = 'red'
        self.high_color = 'green'
        
        self.addParam('low', 'Нижняя граница', kTypeFloat, -100, 100)
        self.addParam('low_color', 'Цвет', kTypeColor)
        self.addParam('high', 'Верхняя граница', kTypeFloat, -100, 100, 
                      validator=lambda x: 'Верхняя граница должна быть больше нижней' if x <= self.low else None)
        self.addParam('high_color', 'Цвет', kTypeColor)
        self.addParam('n', 'n', kTypeInt, 1, 1000)
        
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(self.low, self.low_color), (self.high, self.high_color), (0, 'white')]
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