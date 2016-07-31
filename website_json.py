__author__ = 'Laurent'

import sys, locale, os, re, json
from PyQt5 import QtGui, QtCore, QtWidgets, uic

script_directory = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(os.path.join(script_directory, 'website_mongo.ui'))

localDir = "F:/Documents/Enseignement/Corot/"

try:
    with open(os.path.join(localDir, 'dict.json')) as json_file:
        json_list = json.load(json_file)
except:
    json_list = []


class FileWidget(QtWidgets.QGroupBox):
    def __init__(self, file_dict, parent):
        super(FileWidget, self).__init__(file_dict['title'], parent)
        self.fileChooserWidget = QtWidgets.QPushButton()
        q = next((item for item in json_list if item['title'] == file_dict['title']), None)
        if q:
            self.file_dict = q
        else:
            self.file_dict = file_dict
            json_list.append(self.file_dict)
        if 'url' in file_dict:
            self.fileChooserWidget.setText(file_dict['url'])
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.fileChooserWidget)

    def select_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choisir un fichier...', localDir)
        if filename:
            filename = os.path.relpath(filename, localDir).replace('\\', '/')
            self.fileChooserWidget.setText(filename)
            self.file_dict.update({'url': filename})
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')


class CheckWidget(QtWidgets.QWidget):
    def __init__(self, file_dict, collection, parent):
        super(CheckWidget, self).__init__(parent)
        self.checkbox_widget = QtWidgets.QCheckBox(
            file_dict['subcategory'] if 'category' in file_dict else file_dict['title'])
        q = next((item for item in json_list if item['title'] == file_dict['title']))
        if q:
            self.file_dict = q
            self.checkbox_widget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(file_dict['url']):
            self.checkbox_widget.setDisabled(True)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.checkbox_widget)
        self.parent().transferButton.clicked.connect(self.transfer)
        self.checkbox_widget.stateChanged.connect(lambda _: json_list.append(
            self.file_dict) if self.checkbox_widget.checkState() == QtCore.Qt.Checked else json_list.remove(self.file_dict))


class MultipleCheckWidget(QtWidgets.QGroupBox):
    def __init__(self, name, file_dict_list, collection, parent):
        super(MultipleCheckWidget, self).__init__(name, parent)
        layout = QtWidgets.QHBoxLayout(self)
        for file_dict in file_dict_list:
            layout.addWidget(CheckWidget(file_dict, collection, parent))


class LinkWidget(QtWidgets.QWidget):
    def __init__(self, link_dict, collection, parent):
        super(LinkWidget, self).__init__(parent)
        self.link_dict = link_dict
        self.collection = collection
        name_widget = QtWidgets.QLineEdit(link_dict['name'])
        name_widget.home(True)
        name_widget.deselect()
        name_widget.textChanged.connect(lambda text, link_dict=link_dict: link_dict.update({'name': text}))
        link_widget = QtWidgets.QLineEdit(link_dict['link'])
        link_widget.home(True)
        link_widget.deselect()
        link_widget.textChanged.connect(lambda text, link_dict=link_dict: link_dict.update({'link': text}))
        icon_widget = QtWidgets.QComboBox()
        icons = ["GeoGebra", "Flash", "JavaScript", "Python"]
        icon_widget.addItems(icons)
        icon_widget.setCurrentIndex(icon_widget.findText(link_dict['icon']))
        icon_widget.currentIndexChanged.connect(lambda index: link_dict.update({'icon': icon_widget.currentText()}))
        self.check = QtWidgets.QCheckBox()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(name_widget)
        layout.addWidget(link_widget)
        layout.addWidget(icon_widget)
        layout.addWidget(self.check)
        self.parent().transferButton.clicked.connect(self.transfer)

    def transfer(self):
        self.collection.update_one({'name': self.file_dict['name']}, {'$set': self.file_dict}, upsert=True)

    def remove(self):
        self.collection.delete_one(self.file_dict)


class ScheduleWidget(QtWidgets.QWidget):
    def __init__(self, schedule_dict, collection, parent):
        super(ScheduleWidget, self).__init__(parent)
        self.collection = collection
        name_widget = QtWidgets.QLineEdit(schedule_dict['name'])
        name_widget.home(True)
        name_widget.deselect()
        name_widget.textChanged.connect(lambda text, schedule_dict=schedule_dict: schedule_dict.update({'name': text}))
        person_widget = QtWidgets.QLineEdit(schedule_dict['person'])
        person_widget.home(True)
        person_widget.deselect()
        person_widget.textChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'person': text}))
        date_widget = QtWidgets.QDateTimeEdit(
            QtCore.QDate.fromString(schedule_dict['date'], format=QtCore.Qt.DefaultLocaleLongDate))
        date_widget.setCalendarPopup(True)
        date_widget.dateChanged.connect(
            lambda date, schedule_dict=schedule_dict: schedule_dict.update(
                {'date': date.toString(QtCore.Qt.DefaultLocaleLongDate)}))
        file_widget = QtWidgets.QComboBox()
        file_widget.addItems(os.listdir('ADS'))
        file_widget.setCurrentIndex(file_widget.findText(schedule_dict['filename']))
        file_widget.currentIndexChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'filename': text}))
        self.check = QtWidgets.QCheckBox()
        layout = QtWidgets.QHBoxLayout(self)
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
        for title in ('Colloscope', 'Emploi du temps', 'Planning des DS'):
            self.formVieClasse.addWidget(FileWidget({'title': title, 'category': 'VieClasse'}, self))

        for name in ('Notes premier semestre', 'Notes second semestre'):
            self.formNotes.addWidget(FileWidget({'title': title}, db.notes, self))

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
    app = QtWidgets.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
