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
from indicators.base import Indicator, kTypeInt, addIndicator,\
    windowAverage

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