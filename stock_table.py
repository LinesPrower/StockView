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
from PyQt4 import QtGui, QtCore
from stock import DataEntry
import common as cmn

class StockTableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, data : [DataEntry]):
        QtCore.QAbstractTableModel.__init__(self)
        self.data = data
        
    def rowCount(self, _dummy):
        return len(self.data)
    
    def columnCount(self, _dummy):
        return 7
    
    def headerData(self, section, orient, role):
        if role == QtCore.Qt.DisplayRole and orient == QtCore.Qt.Horizontal:
            return ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Vol'][section]
    
    def data(self, idx, role):
        row = idx.row()
        e = self.data[row]
        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return
        col = idx.column()
        
        def split_num(x):
            return x // 10000, x // 100 % 100, x % 100
        
        def get():
            if col == 0:
                y, m, d = split_num(e.date)
                if y < 100:
                    y += 1900 if y > 50 else 2000
                return '%02d.%02d.%04d' % (d, m, y)
            if col == 1:
                h, m, s = split_num(e.time)
                return '%02d:%02d:%02d' % (h, m, s)
            if col == 2:
                return e.open
            if col == 3:
                return e.high
            if col == 4:
                return e.low
            if col == 5:
                return e.close
            if col == 6:
                return e.vol
        return str(get())
    
    def flags(self, idx):
        col = idx.column()
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if col >= 2:
            flags = flags | QtCore.Qt.ItemIsEditable
        return flags
    
    def setData(self, idx, value, role):
        row = idx.row()
        col = idx.column()
        e = self.data[row]
        if role == QtCore.Qt.EditRole:
            try:
                x = float(value)
            except:
                return False
            if col == 2:
                e.open = x
            if col == 3:
                e.high = x
            if col == 4:
                e.low = x
            if col == 5:
                e.close = x
            if col == 6:
                e.vol = x
            return True
            
        return QtCore.QAbstractTableModel.setData(self, idx, value, role)


class StockDataDialog(cmn.Dialog):
    
    def __init__(self, data):
        cmn.Dialog.__init__(self, cmn.APP_NAME, 'StockDataTable', 'Табличные данные')
        layout = QtGui.QTableView(self)
        layout.setModel(StockTableModel(data))
        self.resize(650, 500)
        self.setDialogLayout(layout, lambda: None, has_statusbar=False, close_btn=True)

if __name__ == '__main__':
    pass