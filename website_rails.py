__author__ = 'Laurent'

import sys, locale, os, re
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from subprocess import check_output

script_directory = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(os.path.join(script_directory, 'website_rails.ui'))

dburl = check_output("heroku config:get DATABASE_URL -a website-mpsi", shell=True).decode().replace("postgres://",
                                                                                                    "postgresql+psycopg2://")
engine = create_engine(dburl)
Base = automap_base()
Base.prepare(engine, reflect=True)
Pdfs = Base.classes.pdfs
session = Session(engine)

localDir = "F:/Documents/Enseignement/Corot/"
remotepath = "https://webdav.cubby.com/Enseignement/Corot/"


class FileWidget(QtWidgets.QGroupBox):
    def __init__(self, file_item, parent):
        super(FileWidget, self).__init__(file_item.title, parent)
        self.fileChooserWidget = QtWidgets.QPushButton()
        q = session.query(Pdfs).filter(Pdfs.category == file_item.category, Pdfs.title == file_item.title).first()
        self.file_item = q if q else file_item
        if self.file_item.url:
            self.fileChooserWidget.setText(self.file_item.url)
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
        self.fileChooserWidget.clicked.connect(self.select_file)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.fileChooserWidget)
        self.parent().transferButton.clicked.connect(self.transfer)

    def select_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Choisir un fichier...', localDir)[0]
        if filename:
            print(filename)
            filename = os.path.relpath(filename, localDir).replace('\\', '/')
            url = os.path.join(remotepath, filename)
            self.fileChooserWidget.setText(url)
            self.file_item.url = url
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')

    def transfer(self):
        session.merge(self.file_item)


class CheckWidget(QtWidgets.QWidget):
    def __init__(self, file_item, parent):
        super(CheckWidget, self).__init__(parent)
        q = session.query(Pdfs).filter(Pdfs.category == file_item.category, Pdfs.url == file_item.url).first()
        self.file_item = q if q else file_item
        self.checkbox_widget = QtWidgets.QCheckBox(file_item.subcategory if file_item.subcategory else file_item.title)
        if q:
            self.checkbox_widget.setCheckState(QtCore.Qt.Checked)
        filename = os.path.join(localDir, os.path.relpath(self.file_item.url, remotepath))
        if not os.path.exists(filename):
            self.checkbox_widget.setDisabled(True)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.checkbox_widget)
        self.parent().transferButton.clicked.connect(self.transfer)

    def transfer(self):
        if self.checkbox_widget.checkState() == QtCore.Qt.Checked:
            session.merge(self.file_item)
        else:
            session.delete(self.file_item)


class MultipleCheckWidget(QtWidgets.QGroupBox):
    def __init__(self, title, list, parent):
        super(MultipleCheckWidget, self).__init__(title, parent)
        layout = QtWidgets.QHBoxLayout(self)
        for item in list:
            layout.addWidget(CheckWidget(item, parent))


class LinkWidget(QtWidgets.QWidget):
    def __init__(self, link_dict, collection, parent):
        super(LinkWidget, self).__init__(parent)
        self.link_dict = link_dict
        self.collection = collection
        title_widget = QtWidgets.QLineEdit(link_dict['title'])
        title_widget.home(True)
        title_widget.deselect()
        title_widget.textChanged.connect(lambda text, link_dict=link_dict: link_dict.update({'title': text}))
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
        layout.addWidget(title_widget)
        layout.addWidget(link_widget)
        layout.addWidget(icon_widget)
        layout.addWidget(self.check)
        self.parent().transferButton.clicked.connect(self.transfer)

    def transfer(self):
        self.collection.update_one({'title': self.file_dict['title']}, {'$set': self.file_dict}, upsert=True)

    def remove(self):
        self.collection.delete_one(self.file_dict)


class ScheduleWidget(QtWidgets.QWidget):
    def __init__(self, schedule_dict, collection, parent):
        super(ScheduleWidget, self).__init__(parent)
        self.collection = collection
        title_widget = QtWidgets.QLineEdit(schedule_dict['title'])
        title_widget.home(True)
        title_widget.deselect()
        title_widget.textChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'title': text}))
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
        file_widget.setCurrentIndex(file_widget.findText(schedule_dict['url']))
        file_widget.currentIndexChanged.connect(
            lambda text, schedule_dict=schedule_dict: schedule_dict.update({'url': text}))
        self.check = QtWidgets.QCheckBox()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(title_widget)
        layout.addWidget(person_widget)
        layout.addWidget(date_widget)
        layout.addWidget(file_widget)
        layout.addWidget(self.check)

    def transfer(self):
        self.collection.update_one({'title': self.file_dict['title']}, {'$set': self.file_dict}, upsert=True)

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
            self.formVieClasse.addWidget(FileWidget(Pdfs(title=title, category="VieClasse"), self))

        for title in ('Notes premier semestre', 'Notes second semestre'):
            self.formNotes.addWidget(FileWidget(Pdfs(title=title, category="VieClasse"), self))

        i = 0
        for title in sorted(os.listdir('DS')):
            if 'DS' in title and os.path.isdir('DS/' + title):
                self.formDS.addWidget(MultipleCheckWidget(title, [
                    Pdfs(title=title, category='DS', subcategory='enonce',
                         url=os.path.join(remotepath, 'DS/' + title + '/' + title + '.pdf')),
                    Pdfs(title=title, category='DS', subcategory='corrige',
                         url=os.path.join(remotepath, 'DS/' + title + '/' + title + '_corrige.pdf'))
                ], self), i / 2, i % 2)
                i += 1

        i = 0
        for title in sorted(os.listdir('DM')):
            if 'DM' in title and os.path.isdir('DM/' + title):
                self.formDM.addWidget(MultipleCheckWidget(title, [
                    Pdfs(title=title, category='DM', subcategory='enonce',
                         url=os.path.join(remotepath, 'DM/' + title + '/' + title + '.pdf')),
                    Pdfs(title=title, category='DM', subcategory='corrige',
                         url=os.path.join(remotepath, 'DM/' + title + '/' + title + '_corrige.pdf'))
                ], self), i / 2, i % 2)
                i += 1

        i = 0
        for name in sorted(os.listdir('Cours')):
            if os.path.isdir('Cours/' + name):
                f = open(localDir + "Cours/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                title = re.search(r'\\titrecours{(.*?)}', s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formCours.addWidget(CheckWidget(Pdfs(title=title, category='Cours', url=os.path.join(remotepath,
                                                                                                          'Cours/' + name + '/' + name + '.pdf')),
                                                     self), i / 4, i % 4)
                i += 1

        i = 0
        for name in sorted(os.listdir('Formulaires')):
            if os.path.isdir('Formulaires/' + name):
                f = open(localDir + "Formulaires/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                title = re.search(r"\\titreformulaire{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formFormulaires.addWidget(CheckWidget(Pdfs(title=title, category='Formulaires',
                                                                url=os.path.join(remotepath,
                                                                                 'Formulaires/' + name + '/' + name + '.pdf')),
                                                           self), i / 4, i % 4)
                i += 1

        i = 0
        for title in sorted(os.listdir('Colles')):
            if 'ProgColles' in title and os.path.isdir('Colles/' + title):
                self.formColles.addWidget(CheckWidget(Pdfs(title=title, category='Colles', url=os.path.join(remotepath,
                                                                                                            'Colles/' + title + '/' + title + '.pdf')),
                                                      self), i / 4, i % 4)
                i += 1

        i = 0
        for title in sorted(os.listdir('Interros')):
            if 'Interro' in title and os.path.isdir('Interros/' + title):
                self.formInterros.addWidget(
                    CheckWidget(Pdfs(title=title, category='Interros',
                                     url=os.path.join(remotepath, 'Interros/' + title + '/' + title + '.pdf')), self),
                    i / 4, i % 4)
                i += 1

        i = 0
        for name in sorted(os.listdir('TD')):
            if os.path.isdir('TD/' + name):
                f = open(localDir + "TD/" + name + "/" + name + ".tex", encoding='utf8')
                s = f.read()
                f.close()
                title = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formTD.addWidget(MultipleCheckWidget(title, [
                    Pdfs(title=title, category='TD', subcategory='enonce',
                         url=os.path.join(remotepath, 'TD/' + name + '/' + name + '.pdf')),
                    Pdfs(title=title, category='TD', subcategory='corrige',
                         url=os.path.join(remotepath, 'TD/' + name + '/' + name + '_corrige.pdf'))], self), i / 4,
                                      i % 4)
                i += 1

    @QtCore.pyqtSlot()
    def on_addADSButton_clicked(self):
        ads = {'title': '', 'person': '', 'category': 'ads', 'date': '', 'url': ''}
        self.formADS.addWidget(ScheduleWidget(ads, "ADS", self))

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
        animation = {'name': '', 'link': '', 'category': 'animation', 'icon': ''}
        self.formAnimations.addWidget(LinkWidget(animation, "Animations", self))

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
