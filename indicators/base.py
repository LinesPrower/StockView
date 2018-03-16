'''
Created on Mar 15, 2018

@author: LinesPrower
'''
from PyQt4 import QtGui
import common as cmn
from common import APP_NAME
import os
import io
import json

kTypeFloat = 0
kTypeInt = 1
kTypeColor = 2

class InvalidParameter(Exception):
    def __init__(self, entry, message):
        self.message = entry.title + ': ' + message

class ClickableLabel(QtGui.QLabel):
    def __init__(self, text, handler):
        QtGui.QLabel.__init__(self, text)
        self.handler = handler
        
    def mousePressEvent(self, ev):
        self.handler()        
    

class ConfigEntry():
    def __init__(self, name, title, ty, min_val=None, max_val=None, validator=None):
        self.name = name
        self.title = title
        self.ty = ty
        self.min_val = min_val
        self.max_val = max_val
        self.validator = validator
        self.ui = None
        
    def makeUI(self, obj):
        if self.ty == kTypeColor:
            self.lbl = ClickableLabel('', self.selectColor)
            self.color = str(self.getval(obj))
            self.lbl.setStyleSheet('QLabel { background-color:%s; }' % self.color)
            self.lbl
            btn = cmn.ToolBtn(cmn.Action(self.lbl, 'Выбрать цвет', 'icons/spectrum.png', self.selectColor))
            self.ui = cmn.HBox([self.lbl, btn], spacing=0)
        else: 
            self.ui = QtGui.QLineEdit()
            self.ui.setText(str(self.getval(obj)))
        
        return self.ui
    
    def selectColor(self):
        t = QtGui.QColorDialog.getColor(QtGui.QColor(self.color), self.lbl, self.title)
        if t.isValid():
            self.color = t.name()
            self.lbl.setStyleSheet('QLabel { background-color:%s; }' % self.color)
        
    def getUIval(self):
        if self.ty == kTypeFloat:
            t = self.ui.text().strip()
            try:
                res = float(t)
            except:
                raise InvalidParameter(self, 'Значение должно быть числом')
        elif self.ty == kTypeInt:
            t = self.ui.text().strip()
            try:
                res = int(t)
            except:
                raise InvalidParameter(self, 'Значение должно быть целым числом')
        elif self.ty == kTypeColor:
            res = self.color
        else:
            raise InvalidParameter(self, 'Недопустимый тип')
        
        if self.min_val != None and res < self.min_val:
            raise InvalidParameter(self, 'Значение должно быть не меньше %s' % self.min_val)
        if self.max_val != None and res > self.max_val:
            raise InvalidParameter(self, 'Значение должно быть не больше %s' % self.max_val)
        if self.validator != None:
            err = self.validator(res)
            if err:
                raise InvalidParameter(self, err)
        return res        
        
    def getval(self, obj):
        return getattr(obj, self.name)
    
    def setval(self, obj, val):
        setattr(obj, self.name, val)


class ConfigDialog(cmn.Dialog):
    
    def __init__(self, obj):
        cmn.Dialog.__init__(self, APP_NAME, 'Config' + obj.__class__.__name__, 'Настройка ' + obj.name)
        layout = cmn.Table([(e.title, e.makeUI(obj)) for e in obj.entries])
        layout = cmn.VBox([layout], align=cmn.kTopAlign)
        self.obj = obj
        self.setDialogLayout(layout, self.doOk)
        
    def doOk(self):
        try:
            values = [e.getUIval() for e in self.obj.entries]
        except InvalidParameter as e:
            self.sbar.showMessage(e.message)
            return
        for v, e in zip(values, self.obj.entries):
            e.setval(self.obj, v)
        self.accept()
    
        
class ConfigurableObject():
    
    def addParam(self, name, title, ty, min_val=None, max_val=None, validator=None):
        self.entries.append(ConfigEntry(name, title, ty, min_val, max_val, validator))
        
    def __init__(self):
        self.entries = []
        
    def getParams(self):
        return {e.name : e.getval(self) for e in self.entries}
    
    def setParams(self, data):
        for e in self.entries:
            if e.name in data:
                e.setval(self, data[e.name])
    
    def getConfigFilename(self):
        return 'configs/%s.json' % self.__class__.__name__  
          
    def loadConfig(self):
        fname = self.getConfigFilename()
        if os.path.isfile(fname):
            with io.open(fname, encoding='utf-8') as f:
                data = json.loads(f.read())
            self.setParams(data)
            
    def configure(self):
        d = ConfigDialog(self)
        if not d.exec_():
            return False
        os.makedirs('configs', exist_ok=True)
        fname = self.getConfigFilename()
        with io.open(fname, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.getParams(), sort_keys=True))
        return True
    
class Indicator(ConfigurableObject):
    
    name = 'Indicator Base'
    
    def __init__(self):
        ConfigurableObject.__init__(self)
        self.ready = False
        self.y_min = 0
        self.y_max = 0
        self.lines = [] # tuples (y, color)
        self.values = []
        self.signals = [] # tuples (idx, bool), True = buy
        
    def compute(self, data):
        self.ready = True
        
    def configure(self):
        if not self.entries:
            QtGui.QMessageBox.information(None, APP_NAME, 'Данный индикатор не имеет настроек')
            return False
        res = ConfigurableObject.configure(self)
        if res:
            self.ready = False
        return res
    
indicators_list = []

def addIndicator(cls):
    indicators_list.append(cls())
    return cls
    
def windowAverage(arr, n):
    res = [None] * len(arr)
    cnt = 0
    sum = 0
    for i, x in enumerate(arr):
        if x == None:
            continue
        sum += x
        cnt += 1
        if cnt >= n:
            res[i] = sum / n
        if cnt >= n:
            sum -= arr[i-n+1]
    return res
    
if __name__ == '__main__':
    print(windowAverage([None, None, 3, 5, 10, 4, 2, 8], 3))