import sys, locale, re, json, io
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from datetime import datetime
from dateutil import parser

scriptDir = QtCore.QDir(__file__)
localDir = QtCore.QDir('F:/Documents/Enseignement/Corot/')


class MyWidget(QtWidgets.QWidget):
    def __init__(self, item, parent, selected):
        super(MyWidget, self).__init__(parent)
        self._item = item
        self._selected = selected

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, value):
        self._item = value

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value


class FileWidget(MyWidget):
    def __init__(self, item, parent, selected=False):
        super(FileWidget, self).__init__(item, parent, selected)
        l = QtWidgets.QHBoxLayout(self)
        box = QtWidgets.QGroupBox(item['title'])
        self.fileChooserWidget = QtWidgets.QPushButton(box)
        if selected:
            self.fileChooserWidget.setText(item.local_path)
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')

        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtWidgets.QHBoxLayout(box)
        layout.addWidget(self.fileChooserWidget)
        l.addWidget(box)

    def select_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choisir un fichier...',
                                                         QtCore.QDir.toNativeSeparators(localDir.absolutePath()))
        if filename:
            filename = localDir.relativeFilePath(filename[0])
            self.fileChooserWidget.setText(filename)
            self.item['localPath'] = filename
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')


class CheckWidget(MyWidget):
    def __init__(self, item, parent, selected=False):
        super(CheckWidget, self).__init__(item, parent, selected)
        layout = QtWidgets.QHBoxLayout(self)
        checkbox_widget = QtWidgets.QCheckBox(item['subcategory'] if 'subcategory' in item else item['title'], self)
        if selected:
            checkbox_widget.setCheckState(QtCore.Qt.Checked)
        if not item['localPath'].exists():
            checkbox_widget.setDisabled(True)
        layout.addWidget(checkbox_widget)


class MultipleCheckWidget(QtWidgets.QGroupBox):
    def __init__(self, title, item_list, parent):
        super(MultipleCheckWidget, self).__init__(title, parent)
        layout = QtWidgets.QHBoxLayout(self)
        for item in item_list:
            layout.addWidget(CheckWidget(item, parent))


class MyTabWidget(QtWidgets.QWidget):
    def __init__(self, category, parent=None):
        super(MyTabWidget, self).__init__(parent)
        grid = QtWidgets.QGridLayout(self)
        categorydir = QtCore.QDir(localDir)
        categorydir.cd(category)
        if category == 'VieClasse':
            for title in ('Colloscope', 'Emploi du temps', 'Planning des DS'):
                grid.addWidget(FileWidget({'category': category, 'title': title}, self))
        elif category in ('DM', 'DS'):
            i = 0
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    grid.addWidget(MultipleCheckWidget(info.baseName(), [
                        {'title': info.baseName(), 'category': category, 'subcategory': 'enonce',
                         'localPath': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf')},
                        {'title': info.baseName(), 'category': category, 'subcategory': 'corrige',
                         'localPath': QtCore.QFileInfo(QtCore.QDir(info.filePath()),
                                                       info.baseName() + '_corrige.pdf')},
                    ], self), i / 4, i % 4)
                i += 1

        elif category in ('Cours', 'Interros'):
            i = 0
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    file = QtCore.QFile(info.filePath() + '/' + info.baseName() + '.tex')
                    file.open(QtCore.QIODevice.ReadOnly)
                    stream = QtCore.QTextStream(file)
                    stream.setCodec('UTF-8')
                    re = QtCore.QRegularExpression('\\\\titre.*{(.*?)}')
                    title = re.match(stream.readAll()).captured(1)
                    grid.addWidget(CheckWidget(
                        {'title': title, 'category': category,
                         'localPath': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf')}, self),
                        i / 4,
                        i % 4)
                i += 1

        elif category in ('TD',):
            i = 0
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    file = QtCore.QFile(info.filePath() + '/' + info.baseName() + '.tex')
                    file.open(QtCore.QIODevice.ReadOnly)
                    stream = QtCore.QTextStream(file)
                    stream.setCodec('UTF-8')
                    re = QtCore.QRegularExpression('\\\\titre.*{(.*?)}')
                    title = re.match(stream.readAll()).captured(1)
                    grid.addWidget(MultipleCheckWidget(title, [
                        {'title': title, 'category': category, 'subcategory': 'enonce',
                         'localPath': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf')},
                        {'title': title, 'category': category, 'subcategory': 'corrige',
                         'localPath': QtCore.QFileInfo(QtCore.QDir(info.filePath()),
                                                       info.baseName() + '_corrige.pdf')},
                    ], self), i / 4, i % 4)
                i += 1


class WebSite(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget(self)
        for category in ('VieClasse', 'DS', 'DM', 'Cours', 'Interros', 'TD'):
            tabs.addTab(MyTabWidget(category), category)
        layout.addWidget(tabs)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtWidgets.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
