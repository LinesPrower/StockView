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
import common as cmn
from common import kProgramName
import io

class AboutDialog(cmn.Dialog):
    
    version = '1.0'
    about_text = '''<b>%s - Программа для технического анализа</b><br/>Версия %s
    <br/>
    Copyright © 2018 Дамир Ахметзянов (linesprower@gmail.com), Лиана Юсупова, Иван Докучаев, Анна Васильева 
    <br/>
    <br/>
    Это свободная программа: вы можете перераспространять её и/или изменять
   её на условиях Стандартной общественной лицензии GNU в том виде, в каком
   она была опубликована Фондом свободного программного обеспечения; либо
   версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
    <br/>
    <br/>
    Данный программный продукт использует пиктограммы из набора 
    <a href="http://p.yusukekamiyamane.com/index.html.en">Fugue Icons</a>
    от Yusuke Kamiyamane по лицензии <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>
    <br/>
    <br/>
    Логотип "Bar chart" от <a href="https://www.freepik.com/">Freepik</a> 
    с сайта <a href="www.flaticon.com">www.flaticon.com</a> 
    ''' % (kProgramName, version)
    
    def __init__(self):
        cmn.Dialog.__init__(self, cmn.APP_NAME, 'AboutBox', _('О программе %s') % kProgramName)
        icon = QtGui.QPixmap('icons/main.png')
        icon_lbl = QtGui.QLabel()
        icon_lbl.setPixmap(icon)
        lbl = QtGui.QLabel(self.about_text)
        lbl.setWordWrap(True)
        lbl.setOpenExternalLinks(True)
        icon_lbl = cmn.VBox([icon_lbl], align=cmn.kTopAlign)
        layout = cmn.HBox([icon_lbl, lbl], 15, 15)
        self.setDialogLayout(layout, lambda: None, has_statusbar=False, close_btn=True, 
                             extra_buttons=[(_('Лицензионное соглашение'), self.showLicense)])
        
    def showLicense(self):
        with io.open('COPYING', encoding='utf-8') as f:
            text = f.read()
        cmn.showReport(_('Лицензионное соглашение'), text)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    d = AboutDialog()
    d.exec_()