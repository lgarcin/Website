__author__ = 'Laurent'

import sys, locale, os, re
from PyQt4 import QtGui, QtCore, uic
from pymongo import MongoClient

script_directory = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(os.path.join(script_directory, 'websiteMPSI.ui'))

client = MongoClient('ds039351.mongolab.com:39351')
db = client.websiteprepa
db.authenticate('lgarcin', 'ua$hu~ka77')

localDir = "F:/Documents/Enseignement/Corot/"


class FileWidget(QtGui.QGroupBox):
    def __init__(self, file_dict, collection, parent):
        super(FileWidget, self).__init__(file_dict['name'], parent)
        self.file_dict = file_dict
        self.collection = collection
        self.fileChooserWidget = QtGui.QPushButton()
        q = collection.find_one({'name': file_dict['name']})
        if q:
            file_dict['filename'] = q['filename']
        if 'filename' in file_dict:
            self.fileChooserWidget.setText(file_dict['filename'])
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.fileChooserWidget)
        self.parent().transferButton.clicked.connect(self.transfer)

    def select_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Choisir un fichier...', localDir)
        if filename:
            filename = os.path.relpath(filename, localDir).replace('\\', '/')
            self.fileChooserWidget.setText(filename)
            self.file_dict.update({'filename': filename})
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')

    def transfer(self):
        if 'filename' in self.file_dict:
            self.collection.update_one({'name': self.file_dict['name']}, {'$set': self.file_dict}, upsert=True)


class CheckWidget(QtGui.QWidget):
    def __init__(self, file_dict, collection, parent):
        super(CheckWidget, self).__init__(parent)
        self.file_dict = file_dict
        self.collection = collection
        f = open(self.file_dict['filename'], mode='rb')
        self.checkbox_widget = QtGui.QCheckBox(file_dict['subtype'] if 'subtype' in file_dict else file_dict['name'])
        if self.collection.find_one({'filename': file_dict['filename']}):
            self.checkbox_widget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(file_dict['filename']):
            self.checkbox_widget.setDisabled(True)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.checkbox_widget)
        self.parent().transferButton.clicked.connect(self.transfer)

    def transfer(self):
        if self.checkbox_widget.checkState() == QtCore.Qt.Checked:
            if 'subtype' in self.file_dict:
                self.collection.update_one({'name': self.file_dict['name'], 'subtype': self.file_dict['subtype']},
                                           {'$set': self.file_dict}, upsert=True)
            else:
                self.collection.update_one({'name': self.file_dict['name']}, {'$set': self.file_dict}, upsert=True)
        else:
            self.collection.delete_one(self.file_dict)


class MultipleCheckWidget(QtGui.QGroupBox):
    def __init__(self, name, file_dict_list, collection, parent):
        super(MultipleCheckWidget, self).__init__(name, parent)
        layout = QtGui.QHBoxLayout(self)
        for file_dict in file_dict_list:
            layout.addWidget(CheckWidget(file_dict, collection, parent))


class LinkWidget(QtGui.QWidget):
    def __init__(self, link_dict, collection, parent):
        super(LinkWidget, self).__init__(parent)
        self.link_dict = link_dict
        self.collection = collection
        name_widget = QtGui.QLineEdit(link_dict['name'])
        name_widget.home(True)
        name_widget.deselect()
        name_widget.textChanged.connect(lambda text, link_dict=link_dict: link_dict.update({'name': text}))
        link_widget = QtGui.QLineEdit(link_dict['link'])
        link_widget.home(True)
        link_widget.deselect()
        link_widget.textChanged.connect(lambda text, link_dict=link_dict: link_dict.update({'link': text}))
        icon_widget = QtGui.QComboBox()
        icons = ["GeoGebra", "Flash", "JavaScript", "Python"]
        icon_widget.addItems(icons)
        icon_widget.setCurrentIndex(icon_widget.findText(link_dict['icon']))
        icon_widget.currentIndexChanged.connect(lambda index: link_dict.update({'icon': icon_widget.currentText()}))
        self.check = QtGui.QCheckBox()
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(name_widget)
        layout.addWidget(link_widget)
        layout.addWidget(icon_widget)
        layout.addWidget(self.check)
        self.parent().transferButton.clicked.connect(self.transfer)

    def transfer(self):
        self.collection.update_one({'name': self.file_dict['name']}, {'$set': self.file_dict}, upsert=True)

    def remove(self):
        self.collection.delete_one(self.file_dict)


class ScheduleWidget(QtGui.QWidget):
    def __init__(self, schedule_dict, collection, parent):
        super(ScheduleWidget, self).__init__(parent)
        self.collection = collection
        name_widget = QtGui.QLineEdit(schedule_dict['name'])
        name_widget.home(True)
        name_widget.deselect()
        name_widget.textChanged.connect(lambda text, schedule_dict=schedule_dict: schedule_dict.update({'name': text}))
        person_widget = QtGui.QLineEdit(schedule_dict['person'])
        person_widget.home(True)
        person_widget.deselect()
        person_widget.textChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'person': text}))
        date_widget = QtGui.QDateTimeEdit(
            QtCore.QDate.fromString(schedule_dict['date'], format=QtCore.Qt.DefaultLocaleLongDate))
        date_widget.setCalendarPopup(True)
        date_widget.dateChanged.connect(
            lambda date, schedule_dict=schedule_dict: schedule_dict.update(
                {'date': date.toString(QtCore.Qt.DefaultLocaleLongDate)}))
        file_widget = QtGui.QComboBox()
        file_widget.addItems(os.listdir('ADS'))
        file_widget.setCurrentIndex(file_widget.findText(schedule_dict['filename']))
        file_widget.currentIndexChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'filename': text}))
        self.check = QtGui.QCheckBox()
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(name_widget)
        layout.addWidget(person_widget)
        layout.addWidget(date_widget)
        layout.addWidget(file_widget)
        layout.addWidget(self.check)

    def transfer(self):
        self.collection.update_one({'name': self.file_dict['name']}, {'$set': self.file_dict}, upsert=True)

    def remove(self):
        self.collection.delete_one(self.file_dict)


class WebSite(form_class, base_class):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        self.setupUi(self)
        self.addADSButton.setIcon(QtGui.QIcon(os.path.join(script_directory, "images/plus_32.ico")))
        self.removeADSButton.setIcon(QtGui.QIcon(os.path.join(script_directory, "images/delete_32.ico")))
        self.addAnimationsButton.setIcon(QtGui.QIcon(os.path.join(script_directory, "images/plus_32.ico")))
        self.removeAnimationsButton.setIcon(QtGui.QIcon(os.path.join(script_directory, "images/delete_32.ico")))
        self.transferButton.setIcon(QtGui.QIcon(os.path.join(script_directory, "images/ftp_64.png")))
        os.chdir(localDir)
        self.fill_forms()

    def fill_forms(self):
        for name in ('Colloscope', 'Emploi du temps', 'Planning des DS'):
            self.formVieClasse.addWidget(FileWidget({'name': name}, db.vieclasse, self))

        for name in ('Notes premier semestre', 'Notes second semestre'):
            self.formNotes.addWidget(FileWidget({'name': name}, db.notes, self))

        i = 0
        for name in sorted(os.listdir('DS')):
            if 'DS' in name and os.path.isdir('DS/' + name):
                self.formDS.addWidget(MultipleCheckWidget(name, [
                    {'name': name, 'subtype': 'enonce', 'filename': 'DS/' + name + '/' + name + '.pdf'},
                    {'name': name, 'subtype': 'corrige',
                     'filename': 'DS/' + name + '/' + name + '_corrige.pdf'}], db.ds, self), i / 2, i % 2)
                i += 1
        i = 0
        for name in sorted(os.listdir('DM')):
            if 'DM' in name and os.path.isdir('DM/' + name):
                self.formDM.addWidget(MultipleCheckWidget(name, [
                    {'name': name, 'subtype': 'enonce', 'filename': 'DM/' + name + '/' + name + '.pdf'},
                    {'name': name, 'subtype': 'corrige',
                     'filename': 'DM/' + name + '/' + name + '_corrige.pdf'}], db.dm, self), i / 2, i % 2)
                i += 1
        i = 0
        for name in sorted(os.listdir('Cours')):
            if os.path.isdir('Cours/' + name):
                f = open(localDir + "Cours/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                titre = re.search(r'\\titrecours{(.*?)}', s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formCours.addWidget(
                    CheckWidget({'name': titre, 'filename': 'Cours/' + name + '/' + name + '.pdf'}, db.cours, self),
                    i / 4, i % 4)
                i += 1
        i = 0
        for name in sorted(os.listdir('Formulaires')):
            if os.path.isdir('Formulaires/' + name):
                f = open(localDir + "Formulaires/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                titre = re.search(r"\\titreformulaire{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formFormulaires.addWidget(
                    CheckWidget(
                        {'name': titre, 'filename': 'Formulaires/' + name + '/' + name + '.pdf'}, db.formulaires, self),
                    i / 4, i % 4)
                i += 1
        i = 0
        for name in sorted(os.listdir('Colles')):
            if 'ProgColles' in name and os.path.isdir('Colles/' + name):
                self.formColles.addWidget(
                    CheckWidget({'name': name, 'filename': 'Colles/' + name + '/' + name + '.pdf'}, db.colles, self),
                    i / 4,
                    i % 4)
                i += 1
        i = 0
        for name in sorted(os.listdir('Interros')):
            if 'Interro' in name and os.path.isdir('Interros/' + name):
                self.formInterros.addWidget(
                    CheckWidget({'name': name, 'filename': 'Interros/' + name + '/' + name + '.pdf'}, db.interros,
                                self),
                    i / 4, i % 4)
                i += 1
        i = 0
        for name in sorted(os.listdir('TD')):
            if os.path.isdir('TD/' + name):
                f = open(localDir + "TD/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formTD.addWidget(MultipleCheckWidget(titre, [
                    {'name': titre, 'subtype': 'enonce', 'filename': 'TD/' + name + '/' + name + '.pdf'},
                    {'name': titre, 'subtype': 'corrige', 'filename': 'TD/' + name + '/' + name + '_corrige.pdf'}],
                                                          db.td, self), i / 4, i % 4)
                i += 1

    @QtCore.pyqtSlot()
    def on_addADSButton_clicked(self):
        ads = {'name': '', 'person': '', 'type': 'ads', 'date': '', 'filename': ''}
        self.formADS.addWidget(ScheduleWidget(ads, db.ads, self))

    @QtCore.pyqtSlot()
    def on_removeADSButton_clicked(self):
        for widget in self.findChildren(ScheduleWidget):
            if widget.check.isChecked():
                widget.remove()
                self.formADS.removeWidget(widget)
                widget.deleteLater()
                self.formADS.update()

    @QtCore.pyqtSlot()
    def on_addAnimationsButton_clicked(self):
        animation = {'name': '', 'link': '', 'type': 'animation', 'icon': ''}
        self.formAnimations.addWidget(LinkWidget(animation, db.animations, self))

    @QtCore.pyqtSlot()
    def on_removeAnimationsButton_clicked(self):
        for widget in self.findChildren(LinkWidget):
            if widget.check.isChecked():
                widget.remove()
                self.formAnimations.removeWidget(widget)
                widget.deleteLater()
                self.formAnimations.update()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtGui.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
