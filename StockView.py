'''
Created on Mar 14, 2018

@author: LinesPrower
'''

from PyQt4 import QtGui, QtCore
import common as cmn
from common import APP_NAME, kProgramName
from stock import StockData, getTicks
import sys

class GraphWidget(QtGui.QWidget):

    def __init__(self, owner, data):
        QtGui.QWidget.__init__(self)
        
        self.panning = False
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor('black'))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        self.data = data        
        self.owner = owner
        self.i0 = 0 # starting index
        
    
    kPixelsPerEntry = 10
    kCenterShift = 5
    kCandleWidth = 3
    
    def getRulerWidth(self):
        return 70
    
    def visibleEntriesCount(self):
        return (self.width() - self.getRulerWidth()) // self.kPixelsPerEntry
        
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
        
        
    def paintEvent(self, ev):
        if not self.data.data:
            return
        
        w = self.width()
        h = self.height()
        ruler_w = self.getRulerWidth()
        ruler_h = 50
        p = QtGui.QPainter(self)
        cl_white = QtGui.QColor('white')
        p.setPen(cl_white)
        
        n = self.visibleEntriesCount()
        i1 = min(len(self.data.data), self.i0 + n)
        self.min_y = min(self.data.data[i].low for i in range(self.i0, i1))
        self.max_y = max(self.data.data[i].high for i in range(self.i0, i1))
        
        h1 = h - ruler_h
        t = h1 / (self.max_y - self.min_y)
        self.y_mpl = -t
        self.y_add = self.min_y * t + h1 
        
        # vertical ruler
        def pt(x, y):
            return QtCore.QPointF(x, self.gety(y))
        
        p.drawLine(ruler_w, 0, ruler_w, h1)
        ticks = getTicks(self.min_y, self.max_y, h1)
        for t in ticks:
            p.drawLine(pt(ruler_w - 7, t), pt(ruler_w, t))
            y = int(self.gety(t))
            p.drawText(0, y - 20, ruler_w - 10, 40, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, str(round(t, 5)))
        dash_pen = QtGui.QPen(QtCore.Qt.DashLine)
        dash_pen.setColor(QtGui.QColor('gray'))
        p.setPen(dash_pen)
        for t in ticks:
            p.drawLine(pt(ruler_w, t), pt(w, t))
        
        def getx(i):
            return ruler_w + (i - self.i0) * self.kPixelsPerEntry + self.kCenterShift
            
        # horizontal ruler
        p.setPen(cl_white)
        p.drawLine(ruler_w, h1, w, h1)
        last = None
        ticks = []
        for i in range(self.i0, i1):
            e = self.data.data[i]
            if not last or e.date != last.date:
                day = e.date % 100
                mon = e.date % 10000 // 100
                s = "%d.%02d" % (day, mon)
                ticks.append((getx(i), s))
            last = e
            
        for t1, t2 in zip(ticks, ticks[1:] + [None]):
            x, s = t1
            textw = t2[0] - t1[0] - 4 if t2 else 100
            p.drawLine(x, h1, x, h1 + 10)                
            p.drawText(x + 2, h1, textw, 30, QtCore.Qt.AlignTop, s)
            
        p.setPen(dash_pen)
        for x, _ in ticks:
            p.drawLine(x, 0, x, h1)
            
        
        p.setPen(cl_white)
        cl_red = QtGui.QColor('red')
        cl_green = QtGui.QColor('green')
        for i in range(self.i0, i1):
            e = self.data.data[i]
            #color = cl_red if e.open > e.close else cl_green
            color = cl_white
            self.drawCandle(p, color, e, getx(i))        
        

class MainW(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(800, 600)
        self.setWindowTitle(kProgramName)
        #self.setWindowIcon(cmn.GetIcon('icons/duckling.png'))
        
        
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
#         self.pbox_scroll = QtGui.QScrollArea(self)
#         self.pbox_scroll.setWidget(self.pbox)
#         self.pbox_scroll.setWidgetResizable(True)
#         self.pbox_scroll.setFocusProxy(self.pbox)
#         layout = self.pbox_scroll
        layout = cmn.VBox([self.pbox, self.sbar], spacing=0)
        self.setCentralWidget(cmn.ensureWidget(layout))

        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(_('Файл'))
        self.act_open = cmn.Action(self, _('Открыть данные котировок...'), 'icons/open.png', self.doOpen, 'Ctrl+O')
        
        fileMenu.addAction(self.act_open)
        fileMenu.addSeparator()
        fileMenu.addAction(cmn.Action(self, _('Exit'), '', self.exitApp))
        
        #helpMenu = menubar.addMenu(_('Help'))
        #helpMenu.addAction(self.act_about)
        self.show()
        self.doOpenRaw(r'Finam_data\GAZP_170314_180314.txt')
    
    def updateScrollbar(self):
        n = self.pbox.visibleEntriesCount()
        m = len(self.pbox.data.data)
        self.sbar.setVisible(n < m)
        if n < m:
            self.sbar.setMinimum(0)
            self.sbar.setMaximum(m - n)
            self.sbar.setPageStep(n)
    
    def exitApp(self):
        if self.closingCheck():
            QtGui.qApp.quit()
            
    def resetUI(self):
        self.updateScrollbar()
        self.pbox.update()

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