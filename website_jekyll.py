import sys, locale, re, json, io
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from datetime import datetime
from natsort import natsorted
from yaml import dump, load

# from git import Repo

scriptDir = QtCore.QDir(__file__)
directory = QtCore.QDir('E:/Documents/Enseignement/Corot2016/')
saveDirectory = QtCore.QDir('E:/Documents/Github/lgarcin.github.io')


def convert_dictionary_to_array(d):
    l = []
    for e in d:
        dd = {'title': e}
        dd.update(d[e])
        l.append(dd)
    return l


def convert_array_to_dictionary(l):
    d = {}
    for e in l:
        title = e['title']
        e.pop('title', None)
        d[title] = e
    return d


class MyWidget(QtWidgets.QWidget):
    def __init__(self, item, parent):
        super(MyWidget, self).__init__(parent)
        self._item = item

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
    def __init__(self, title, item, parent):
        super(FileWidget, self).__init__(item, parent)
        l = QtWidgets.QHBoxLayout(self)
        box = QtWidgets.QGroupBox(title)
        self.fileChooserWidget = QtWidgets.QPushButton(box)
        if 'path' in item:
            self.fileChooserWidget.setText(item['path'].fileName())
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')

        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtWidgets.QHBoxLayout(box)
        layout.addWidget(self.fileChooserWidget)
        l.addWidget(box)

    def select_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choisir un fichier...',
                                                         QtCore.QDir.toNativeSeparators(directory.absolutePath()))
        if filename:
            filename = directory.relativeFilePath(filename[0])
            self.fileChooserWidget.setText(filename)
            self.item['path'] = QtCore.QFileInfo(directory, filename)
            self.item['selected'] = True
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
            self.item['selected'] = False


class CheckWidget(MyWidget):
    def __init__(self, title, item, parent):
        super(CheckWidget, self).__init__(item, parent)
        layout = QtWidgets.QHBoxLayout(self)
        checkbox_widget = QtWidgets.QCheckBox(title, self)
        if item['selected']:
            checkbox_widget.setCheckState(QtCore.Qt.Checked)
        if not item['path'].exists():
            checkbox_widget.setDisabled(True)
        layout.addWidget(checkbox_widget)
        checkbox_widget.stateChanged.connect(lambda _: item.update({'selected': not item['selected']}))


class MultipleCheckWidget(QtWidgets.QGroupBox):
    def __init__(self, title, item, parent):
        super(MultipleCheckWidget, self).__init__(title, parent)
        layout = QtWidgets.QHBoxLayout(self)
        for k, v in item.items():
            layout.addWidget(CheckWidget(k, v, parent))


class DictionaryHandler:
    def __init__(self, directory, saveDirectory):
        self.directory = directory
        self.saveDirectory = saveDirectory
        self.dictionary = {}

    def buildDictionary(self):
        yamlDirectory = QtCore.QDir(self.saveDirectory)
        yamlDirectory.cd('_data')
        yamlFile = QtCore.QFile(yamlDirectory.filePath('pdfs.yml'))
        yamlFile.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        stream = QtCore.QTextStream(yamlFile)
        stream.setCodec('UTF-8')
        yamlDictionary = load(stream.readAll())
        yamlFile.close()
        for category in yamlDictionary:
            yamlDictionary[category] = convert_array_to_dictionary(yamlDictionary[category])

        dd = yamlDictionary['VieClasse'] if 'VieClasse' in yamlDictionary else {}
        categorydir = QtCore.QDir(self.directory)
        categorydir.cd('VieClasse')
        self.dictionary['VieClasse'] = {
            t: {
                'path': QtCore.QFileInfo(categorydir, dd[t]['path']),
                'selected': True} if t in dd and 'path' in dd[t] else {'selected': False} for t in
            ('Emploi du temps', 'Colloscope', 'Planning des DS')
            }
        for category in ('DM', 'DS'):
            categorydir = QtCore.QDir(self.directory)
            categorydir.cd(category)
            d = {}
            self.dictionary[category] = d
            dd = yamlDictionary[category] if category in yamlDictionary else {}
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    d[info.baseName()] = {
                        'Enoncé': {
                            'path': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf'),
                            'selected': info.baseName() in dd and 'Enoncé' in dd[info.baseName()]},
                        'Corrigé': {'path': QtCore.QFileInfo(QtCore.QDir(info.filePath()),
                                                             info.baseName() + '.corrige.pdf'),
                                    'selected': info.baseName() in dd and 'Corrigé' in dd[info.baseName()]}
                    }

        for category in ('Cours', 'Interros', 'Colles', 'Formulaires'):
            categorydir = QtCore.QDir(self.directory)
            categorydir.cd(category)
            d = {}
            self.dictionary[category] = d
            dd = yamlDictionary[category] if category in yamlDictionary else{}
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    file = QtCore.QFile(info.filePath() + '/' + info.baseName() + '.tex')
                    file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
                    stream = QtCore.QTextStream(file)
                    stream.setCodec('UTF-8')
                    re = QtCore.QRegularExpression('\\\\titre.*{(.*?)}')
                    title = re.match(stream.readAll()).captured(1)
                    d[title] = {'path': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf'),
                                'selected': title in dd}

        for category in ('TD',):
            categorydir = QtCore.QDir(self.directory)
            categorydir.cd(category)
            d = {}
            self.dictionary[category] = d
            dd = yamlDictionary[category] if category in yamlDictionary else {}
            for info in categorydir.entryInfoList(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot):
                if info.isDir():
                    file = QtCore.QFile(info.filePath() + '/' + info.baseName() + '.tex')
                    file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
                    stream = QtCore.QTextStream(file)
                    stream.setCodec('UTF-8')
                    re = QtCore.QRegularExpression('\\\\titre.*{(.*?)}')
                    title = re.match(stream.readAll()).captured(1)
                    d[title] = {
                        'Enoncé': {
                            'path': QtCore.QFileInfo(QtCore.QDir(info.filePath()), info.baseName() + '.pdf'),
                            'selected': title in dd and 'Enoncé' in dd[title]},
                        'Corrigé': {'path': QtCore.QFileInfo(QtCore.QDir(info.filePath()),
                                                             info.baseName() + '.corrige.pdf'),
                                    'selected': title in dd and 'Corrigé' in dd[title]}
                    }

    def saveDictionary(self):
        pdfsDirectory = QtCore.QDir(self.saveDirectory)
        pdfsDirectory.cd('pdfs')
        for file in pdfsDirectory.entryList(QtCore.QDir.Files):
            pdfsDirectory.remove(file)

        def copy(d, dd):
            if 'selected' not in d or d['selected'] == True:
                for key in d:
                    if key == 'path':
                        dd[key] = d[key].fileName()
                        QtCore.QFile.copy(d[key].absoluteFilePath(), pdfsDirectory.filePath(d[key].fileName()))
                    elif key != 'selected':
                        dd[key] = d[key]
                    if isinstance(d[key], dict):
                        dd[key] = {}
                        copy(d[key], dd[key])
                        if not dd[key]:
                            dd.pop(key)

        d = {}
        copy(self.dictionary, d)
        yamlDirectory = QtCore.QDir(self.saveDirectory)
        yamlDirectory.cd('_data')
        yamlFile = QtCore.QFile(yamlDirectory.filePath('pdfs.yml'))
        yamlFile.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)
        stream = QtCore.QTextStream(yamlFile)
        stream.setCodec('UTF-8')
        for category in d:
            d[category] = convert_dictionary_to_array(d[category])
        stream << dump(d, default_flow_style=False, allow_unicode=True)
        yamlFile.close()


class MyTabWidget(QtWidgets.QWidget):
    def __init__(self, category, items, parent=None):
        super(MyTabWidget, self).__init__(parent)
        grid = QtWidgets.QGridLayout(self)
        if category == 'VieClasse':
            for k, v in items.items():
                grid.addWidget(FileWidget(k, v, self))
        elif category in ('DM', 'DS', 'TD'):
            i = 0
            for k, v in sorted(items.items()):
                grid.addWidget(MultipleCheckWidget(k, v, self), i / 4, i % 4)
                i += 1
        elif category in ('Cours', 'Interros', 'Colles', 'Formulaires'):
            i = 0
            for k, v in natsorted(items.items()):
                grid.addWidget(CheckWidget(k, v, self), i / 4, i % 4)
                i += 1


class WebSite(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        dh = DictionaryHandler(directory, saveDirectory)
        dh.buildDictionary()
        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget(self)
        for k, v in dh.dictionary.items():
            tabs.addTab(MyTabWidget(k, v, self), k)
        layout.addWidget(tabs)
        saveButton = QtWidgets.QPushButton('Sauvegarder')
        layout.addWidget(saveButton)
        saveButton.clicked.connect(lambda _: dh.saveDictionary())


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtWidgets.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
