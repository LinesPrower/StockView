'''
Created on Mar 14, 2018

@author: LinesPrower
'''

from PyQt4 import QtGui, QtCore
import common as cmn
from common import APP_NAME, kProgramName, kLeftAlign
from stock import StockData, getTicks
import sys
from indicators.base import indicators_list

# these import are needed for the indicators to show up in the combobox
import indicators.roc


kViewCandle = 0
kViewBars   = 1
kViewLinear = 2

class GraphWidget(QtGui.QWidget):
    
    cl_white = QtGui.QColor('white')
    cl_black = QtGui.QColor('black')
    cl_red = QtGui.QColor('red')
    cl_green = QtGui.QColor('green')
    cl_blue = QtGui.QColor('blue')
    dash_pen = QtGui.QPen(QtCore.Qt.DashLine)
    dash_pen.setColor(QtGui.QColor('gray'))
    
    # kBGColor = QtGui.QColor('black')
    kBGColor = QtGui.QColor('white')
    kFGColor = cl_black

    def __init__(self, owner, data):
        QtGui.QWidget.__init__(self)
        
        self.panning = False
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, self.kBGColor)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        self.indicator = None
        self.ruler_h = 50
        self.ruler_w = 70
        
        self.data = data        
        self.owner = owner
        self.i0 = 0 # starting index
        self.view_mode = kViewCandle
        
    
    kPixelsPerEntry = 10
    kCenterShift = 5
    kCandleWidth = 3
    
    def visibleEntriesCount(self):
        return (self.width() - self.ruler_w) // self.kPixelsPerEntry
    
    def compute_y_transform(self, min_y, max_y):
        h1 = self.height() - self.ruler_h
        t = h1 / (max_y - min_y)
        self.y_mpl = -t
        self.y_add = min_y * t + h1
        
    def gety(self, y):
        return y * self.y_mpl + self.y_add
    
    def drawCandle(self, p, color, entry, x):
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
        
        #p.setPen(color)
        p.drawLine(pt(x, entry.low), pt(x, min(entry.open, entry.close)))
        p.drawLine(pt(x, entry.high), pt(x, max(entry.open, entry.close)))
        if entry.open < entry.close:
            p.setBrush(QtCore.Qt.NoBrush)
        else:
            p.setBrush(color)
        p.drawRect(QtCore.QRectF(pt(x - self.kCandleWidth, entry.open),
                                 pt(x + self.kCandleWidth, entry.close)))
        
    def drawBar(self, p, entry, x):
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
        color = self.cl_green if entry.open < entry.close else self.cl_red
        p.setPen(color)
        p.drawLine(pt(x, entry.low), pt(x, entry.high))
        p.drawLine(pt(x - self.kCandleWidth, entry.open), pt(x, entry.open))
        p.drawLine(pt(x + self.kCandleWidth, entry.close), pt(x, entry.close))
        
    def getx(self, i):
        return self.ruler_w + (i - self.i0) * self.kPixelsPerEntry + self.kCenterShift
    
    def drawVerticalRuler(self, p, min_y, max_y):
        
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
        
        h1 = self.height() - self.ruler_h
        w = self.width()
        p.drawLine(self.ruler_w, 0, self.ruler_w, h1)
        ticks = getTicks(min_y, max_y, h1)
        for t in ticks:
            p.drawLine(pt(self.ruler_w - 7, t), pt(self.ruler_w, t))
            y = int(self.gety(t))
            p.drawText(0, y - 20, self.ruler_w - 10, 40, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, str(round(t, 5)))
        p.setPen(self.dash_pen)
        for t in ticks:
            p.drawLine(pt(self.ruler_w, t), pt(w, t))
        
        
    def drawIndicator(self, p):
        if not self.indicator or not self.indicator.ready:
            return
        n = self.visibleEntriesCount()
        i0 = max(self.i0 - 1, 0)
        i1 = min(len(self.indicator.values), self.i0 + n + 1)
        y_min = min([x for x in self.indicator.values[i0:i1] if x != None] + [self.indicator.y_min])
        y_max = max([x for x in self.indicator.values[i0:i1] if x != None] + [self.indicator.y_max])
        self.compute_y_transform(y_min, y_max)
        p.setPen(self.cl_blue)
        
        def pti(i, y):
            return QtCore.QPointF(self.getx(i), self.gety(y))
        
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
        
        for i in range(i0, i1-1):
            y1 = self.indicator.values[i]
            y2 = self.indicator.values[i+1]
            if y1 != None and y2 != None:
                p.drawLine(pti(i, y1), pti(i+1, y2))
                
        w = self.width()
        for y, col in self.indicator.lines:
            p.setPen(QtGui.QColor(col))
            p.drawLine(pt(self.ruler_w, y), pt(w, y))
            
        p.setPen(self.cl_blue)        
        self.drawVerticalRuler(p, y_min, y_max)
            
        # signals
        self.compute_y_transform(self.y_min, self.y_max)
        for i, is_buy in self.indicator.signals:
            if not i0 <= i <= i1:
                continue
            x = self.getx(i)
            e = self.data.data[i]
            y = self.gety(e.close)
            if is_buy:
                p.setPen(self.cl_green)
                p.setBrush(self.cl_green)
                #y = self.gety(min(e.open, e.close))
                dy = 15
            else:
                p.setPen(self.cl_red)
                p.setBrush(self.cl_red)
                #y = self.gety(max(e.open, e.close))
                dy = -15
            p.drawConvexPolygon(QtCore.QPointF(x, y),
                                QtCore.QPointF(x - 9, y + dy),
                                QtCore.QPointF(x + 9, y + dy))
        
        
    def paintEvent(self, ev):
        if not self.data.data:
            return
        
        w = self.width()
        h = self.height()
        ruler_w = self.ruler_w
        h1 = h - self.ruler_h
        p = QtGui.QPainter(self)
        p.setPen(self.kFGColor)
        
        n = self.visibleEntriesCount()
        i1 = min(len(self.data.data), self.i0 + n)
        min_y = min(self.data.data[i].low for i in range(self.i0, i1))
        max_y = max(self.data.data[i].high for i in range(self.i0, i1))
        
        self.compute_y_transform(min_y, max_y)
        self.y_min = min_y
        self.y_max = max_y 
        
        # vertical ruler
        if not self.indicator:
            self.drawVerticalRuler(p, min_y, max_y)
            
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
            
        # horizontal ruler
        p.setPen(self.kFGColor)
        p.drawLine(ruler_w, h1, w, h1)
        last = None
        ticks = []
        for i in range(self.i0, i1):
            e = self.data.data[i]
            if not last or e.date != last.date:
                day = e.date % 100
                mon = e.date % 10000 // 100
                s = "%d.%02d" % (day, mon)
                ticks.append((self.getx(i), s))
            last = e
            
        for t1, t2 in zip(ticks, ticks[1:] + [None]):
            x, s = t1
            textw = t2[0] - t1[0] - 4 if t2 else 100
            p.drawLine(x, h1, x, h1 + 10)                
            p.drawText(x + 2, h1, textw, 30, QtCore.Qt.AlignTop, s)
            
        p.setPen(self.dash_pen)
        for x, _ in ticks:
            p.drawLine(x, 0, x, h1)
            
        
        p.setPen(self.kFGColor)
        last = None
        for i in range(self.i0, i1):
            e = self.data.data[i]
            if self.view_mode == kViewCandle:
                #color = cl_red if e.open > e.close else cl_green
                color = self.kFGColor
                self.drawCandle(p, color, e, self.getx(i))
            elif self.view_mode == kViewBars:
                self.drawBar(p, e, self.getx(i))
            else:
                if last:
                    p.drawLine(pt(self.getx(i-1), last.close), pt(self.getx(i), e.close))
                
            last = e
        self.drawIndicator(p)
        
        # name
        p.setPen(self.kFGColor)
        p.drawText(self.ruler_w + 10, 20, self.data.name)
        
    def wheelEvent(self, ev):
        self.owner.sbar.wheelEvent(ev)
    
    def mousePressEvent(self, ev):
        if not self.owner.sbar.isVisible():
            return
        self.panning = True
        self.pan_start_x = ev.globalPos().x()
        self.pan_start_value = self.owner.sbar.value()
    
    def mouseMoveEvent(self, ev):
        if not self.panning:
            return
        x = ev.globalPos().x()
        delta = (self.pan_start_x - x) // self.kPixelsPerEntry
        self.owner.sbar.setSliderPosition(self.pan_start_value + delta)
        
    def mouseReleaseEvent(self, ev):
        self.panning = False       
        

class MainW(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(800, 600)
        self.setWindowTitle(kProgramName)
        self.setWindowIcon(cmn.GetIcon('icons/main.png'))
        
        
        #self.check_results = CheckResultsPanel(self)
        #self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.check_results)

        s = QtCore.QSettings('LinesPrower', APP_NAME)
        t = s.value("mainwnd/geometry")
        if t:
            self.restoreGeometry(t)
        t = s.value("mainwnd/dockstate")
        if t:
            self.restoreState(t, 0)
            
        self.data = StockData()
        self.pbox = GraphWidget(self, self.data)
        
        self.sbar = QtGui.QScrollBar(QtCore.Qt.Horizontal, self)
        
        def seti0(i0):
            self.pbox.i0 = i0
            self.pbox.update()
        
        self.sbar.valueChanged.connect(seti0)
        
        self.view_mode_cbx = QtGui.QComboBox()
        self.view_mode_cbx.addItems(['Свечи', "Бары", "Линейный"])
        
        def setViewMode(mode):
            self.pbox.view_mode = mode
            self.pbox.update()
            
        self.indicator_checkbox = QtGui.QCheckBox('Индикатор')
        self.indicator_checkbox.toggled.connect(self.updateUI)
        self.indicator_cbx = QtGui.QComboBox()
        self.indicator_cbx.addItems([x.name for x in indicators_list])
        self.indicator_cbx.currentIndexChanged.connect(self.updateUI)
        
        self.view_mode_cbx.currentIndexChanged.connect(setViewMode)
        toolbar = cmn.HBox([QtGui.QLabel(' Вид графика'), 
                            self.view_mode_cbx,
                            QtGui.QLabel('   '),
                            self.indicator_checkbox,
                            self.indicator_cbx,
                            cmn.ToolBtn(cmn.Action(self, 'Настройка индикатора', 'icons/wrench.png', self.doConfigure, 'F7'))
                            ], align=kLeftAlign)
                
        layout = cmn.VBox([toolbar, self.pbox, self.sbar], spacing=0)
        self.setCentralWidget(cmn.ensureWidget(layout))

        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(_('Файл'))
        self.act_open = cmn.Action(self, _('Открыть данные котировок...'), 'icons/open.png', self.doOpen, 'Ctrl+O')
        
        fileMenu.addAction(self.act_open)
        fileMenu.addSeparator()
        fileMenu.addAction(cmn.Action(self, _('Выход'), '', self.exitApp))
        
        #helpMenu = menubar.addMenu(_('Help'))
        #helpMenu.addAction(self.act_about)
        self.show()
        self.doOpenRaw(r'Finam_data\GAZP_170314_180314.txt')
    
    def doConfigure(self):
        ind = indicators_list[self.indicator_cbx.currentIndex()]
        if ind.configure():
            self.updateUI()
        
    def updateUI(self):
        if self.indicator_checkbox.isChecked():
            self.pbox.indicator = indicators_list[self.indicator_cbx.currentIndex()]
            if not self.pbox.indicator.ready:
                self.pbox.indicator.compute(self.data.data)
        else:
            self.pbox.indicator = None
        self.pbox.update()
    
    def updateScrollbar(self):
        n = self.pbox.visibleEntriesCount()
        m = len(self.pbox.data.data)
        self.sbar.setVisible(n < m)
        if n < m:
            self.sbar.setMinimum(0)
            self.sbar.setMaximum(m - n)
            self.sbar.setPageStep(n)
    
    def exitApp(self):
        QtGui.qApp.quit()
            
    def resetUI(self): # called when data changes
        for ind in indicators_list:
            ind.ready = False
        self.updateScrollbar()
        self.updateUI()

    def doOpenRaw(self, fname):
        try:
            self.data.load(fname)
        except:
            QtGui.QMessageBox.critical(self, kProgramName, _('An error occurred while opening file "%s"') % fname)
            raise
        self.resetUI()
        
    def doOpen(self):
        fname = cmn.getOpenFileName(self, 'es', _('Open File'), 'Файлы котировок (*.txt)')
        if fname:
            self.doOpenRaw(fname)
            
    def resizeEvent(self, ev):
        self.updateScrollbar()
        return QtGui.QMainWindow.resizeEvent(self, ev)

    def closeEvent(self, event):
        s = QtCore.QSettings('LinesPrower', APP_NAME)
        s.setValue("mainwnd/geometry", self.saveGeometry())
        s.setValue('mainwnd/dockstate', self.saveState(0))

def main():    
    app = QtGui.QApplication(sys.argv)
    _ = MainW()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()