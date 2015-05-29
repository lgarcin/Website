__author__ = 'Laurent'

import sys, locale, os, re, json, io
from PyQt4 import QtGui, QtCore, uic
from datetime import datetime
from dateutil import parser
from pymongo import MongoClient
import gridfs

script_directory = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(os.path.join(scriptdir, 'websitePrepa.ui'))

client = MongoClient('ds039351.mongolab.com:39351')
db = client.websiteprepa
db.authenticate('lgarcin', 'ua$hu~ka77')
fs = gridfs(db)


class ChooseFileWidget:
    def __init__(self, file_dict, parent=None):
        super(ChooseFileWidget, self).__init__(parent)
        self.file_dict = file_dict
        name_widget = QtGui.QLabel(file_dict['type'])
        self.fileChooserWidget = QtGui.QPushButton()
        if 'path' in file_dict:
            self.fileChooserWidget.setText(file_dict['filename'])
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(name_widget)
        layout.addWidget(self.fileChooserWidget)

    def select_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Choisir un fichier...')
        if filename:
            self.fileChooserWidget.setText(filename)
            self.file_dict.update({'filename': filename})
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')


class CheckWidget:
    def __init__(self, file_dict, parent=None):
        super(CheckWidget, self).__init__(parent)
        self.file_dict = file_dict
        self.checkboxWidget = QtGui.QCheckBox(file_dict['type'])
        self.checkboxWidget.stateChanged.connect(
            lambda state: file_dict.update({'to_upload:True'} if state == QtCore.Qt.Checked else {'to_upload:True'}))
        if 'filename' in file_dict and fs.exists({'filename': file_dict['filename']}):
            self.checkboxWidget.setCheckState(QtCore.Qt.Checked)
        if 'missing' in file_dict:
            self.checkboxWidget.setDisabled(True)


class MultipleCheckWidget:
    def __init__(self, name, file_dict_list, parent=None):
        super(MultipleCheckWidget, self).__init__(parent)
        name_widget = QtGui.QLabel(name)
        check_widgets = [CheckWidget(file_dict) for file_dict in file_dict_list]
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(name_widget)
        for check_widget in check_widgets:
            layout.addWidget(check_widget)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtGui.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
