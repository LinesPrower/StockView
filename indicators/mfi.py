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
from indicators.base import Indicator, kTypeFloat, kTypeInt, addIndicator

@addIndicator
class MFI(Indicator):
    
    name = 'MFI'
    
    def __init__(self):
        Indicator.__init__(self)
        self.n = 14
        self.low = 20
        self.high = 80
        self.addParam('n', 'Число периодов', kTypeInt, 1, 1000)
        self.addParam('low', 'Нижняя граница', kTypeFloat, 0, 100)
        self.addParam('high', 'Верхняя граница', kTypeFloat, 0, 100, 
                      validator=lambda x: 'Верхняя граница должна быть больше нижней' if x <= self.low else None)    
        self.loadConfig()
        
    def compute(self, data):
        self.values = []
        self.signals = []
        self.lines = [(self.low, 'red'), (self.high, 'green')]
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
            if x < self.low:
                sig = True
            elif x > self.high:
                sig = False
            if sig != None and sig != last_signal:
                self.signals.append((i, sig))
                last_signal = sig            
            
        self.ready = True
        
        
    
def main():
    pass

if __name__ == '__main__':
    main()