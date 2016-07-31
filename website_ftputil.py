__author__ = 'Laurent'

import sys, locale, os, re
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from pyquery import PyQuery as pq
from datetime import datetime
from time import sleep
from ftputil import FTPHost

scriptdir = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(scriptdir + '/website_ftputil.ui')


def read(filename):
    try:
        with open(filename, "r", encoding='utf8') as f:
            s = f.read()
            f.close()
    except:
        with open(filename, "r") as f:
            s = f.read()
            f.close()
    return s


class WebSite(form_class, base_class):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        self.setupUi(self)
        self.removeADSButton.setIcon(QtGui.QIcon(scriptdir + "/images/delete_32.ico"))
        self.addADSButton.setIcon(QtGui.QIcon(scriptdir + "/images/plus_32.ico"))
        self.removeAnimationsButton.setIcon(QtGui.QIcon(scriptdir + "/images/delete_32.ico"))
        self.addAnimationsButton.setIcon(QtGui.QIcon(scriptdir + "/images/plus_32.ico"))
        self.transferButton.setIcon(QtGui.QIcon(scriptdir + "/images/ftp_64.png"))
        self.saveButton.setIcon(QtGui.QIcon(scriptdir + "/images/save_64.png"))
        self.reloadButton.setIcon(QtGui.QIcon(scriptdir + "/images/reload_64.png"))
        self.rootdir = "F:/Documents/Enseignement/Corot"
        os.chdir(self.rootdir)
        self.load()

    def load(self):
        with open("index.html", encoding="utf8") as f:
            self.html = pq(f.read())
        for form in (
                self.formDS, self.formDM, self.formColles, self.formCours, self.formInterros, self.formTD,
                self.formInfo,
                self.formTDInfo, self.formTPInfo, self.formADS, self.formFormulaires):
            if form is not None:
                while form.count():
                    item = form.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
        self.populate()

    def populate(self):
        self.populateDS()
        self.populateDM()
        self.populateColles()
        self.populateCours()
        self.populateInterros()
        self.populateTD()
        self.populateInfo()
        self.populateSlidesInfo()
        self.populateTDInfo()
        self.populateTPInfo()
        self.populateDSInfo()
        self.populateADS()
        self.populateFormulaires()
        self.populateAnimations()

    def update(self):
        self.message.setInformativeText("Mise à jour des fichiers HTML")
        self.updateDS()
        self.updateDM()
        self.updateColles()
        self.updateCours()
        self.updateInterros()
        self.updateTD()
        self.updateInfo()
        self.updateSlidesInfo()
        self.updateTDInfo()
        self.updateTPInfo()
        self.updateDSInfo()
        self.updateADS()
        self.updateFormulaires()
        self.updateAnimations()

    def writeLocalHTML(self):
        self.message.setInformativeText("Enregistement des fichiers HTML")
        with open("index.html", "w", encoding='utf8') as f:
            f.write('<!DOCTYPE html><html>')
            f.write(self.html.html(method='html'))
            f.write('</html>')
            f.close()

    def transfer(self):
        self.message.setInformativeText("Synchronisation avec le serveur FTP")
        self.thread = TransferThread(self.localFileList())
        self.thread.start()
        self.thread.message.connect(self.updateMessage)

    def localFileList(self):
        list = []
        for d in ('admin', 'css', 'js', 'Notes', 'Animations', 'img', 'jars', 'fonts'):
            for dirpath, dirnames, filenames in os.walk(d):
                for filename in filenames:
                    list.append(os.path.join(dirpath, filename).replace('\\', '/'))
        for file in (".htaccess", "index.html", "robots.txt", "favicon.ico", "404.html"):
            list.append(file)
        for form in (self.formDS, self.formDM, self.formTD, self.formTDInfo, self.formTPInfo):
            if form.count() != 0:
                for i in range(form.rowCount()):
                    if form.itemAtPosition(i, 1).widget().isChecked():
                        file = form.itemAtPosition(i, 1).widget().objectName()
                        list.append(file)
                    if form.itemAtPosition(i, 2).widget().isChecked():
                        file = form.itemAtPosition(i, 2).widget().objectName()
                        list.append(file)
        for form in (self.formColles, self.formCours, self.formInterros, self.formInfo, self.formFormulaires):
            for i in range(form.count()):
                if form.itemAt(i).widget().isChecked():
                    file = form.itemAt(i).widget().objectName()
                    list.append(file)
        for i in range(self.formADS.rowCount()):
            try:
                file = 'ADS/' + self.formADS.itemAtPosition(i, 3).widget().currentText()
                list.append(file)
            except:
                pass
        for tag in self.html('a[href]'):
            file = pq(tag).attr("href")
            if os.path.isfile(file):
                if file not in list:
                    list.append(file)
        return list

    def populateDS(self):
        i = 0
        for name in os.listdir('DS'):
            if 'DS' in name and os.path.isdir('DS/' + name):
                self.formDS.addWidget(QtWidgets.QLabel(name), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'DS/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDS.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'DS/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDS.addWidget(checkbox, i, 2)
                i += 1

    def populateDM(self):
        i = 0
        for name in os.listdir('DM'):
            if 'DM' in name and os.path.isdir('DM/' + name):
                self.formDM.addWidget(QtWidgets.QLabel(name), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'DM/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDM.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'DM/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDM.addWidget(checkbox, i, 2)
                i += 1

    def populateColles(self):
        i = 0
        for name in os.listdir('Colles'):
            if "ProgColles" in name and os.path.isdir('Colles/' + name):
                checkbox = QtWidgets.QCheckBox(name)
                path = 'Colles/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formColles.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateCours(self):
        i = 0
        for name in os.listdir('Cours'):
            if os.path.isdir('Cours/' + name):
                s = read(self.rootdir + "/Cours/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                checkbox = QtWidgets.QCheckBox(titre)
                path = 'Cours/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formCours.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateInterros(self):
        i = 0
        for name in os.listdir('Interros'):
            if "Interro" in name and os.path.isdir('Interros/' + name):
                checkbox = QtWidgets.QCheckBox(name)
                path = 'Interros/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formInterros.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateTD(self):
        i = 0
        for name in os.listdir('TD'):
            if os.path.isdir('TD/' + name):
                s = read(self.rootdir + "/TD/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formTD.addWidget(QtWidgets.QLabel(titre), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'TD/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTD.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'TD/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTD.addWidget(checkbox, i, 2)
                i += 1

    def populateInfo(self):
        if not os.path.exists('Informatique'):
            return
        i = 0
        for name in os.listdir('Informatique'):
            if os.path.isdir('Informatique/' + name):
                s = read(self.rootdir + "/Informatique/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                checkbox = QtWidgets.QCheckBox(titre)
                path = 'Informatique/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formInfo.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateSlidesInfo(self):
        if not os.path.exists('SlidesInfo'):
            return
        i = 0
        for name in os.listdir('SlidesInfo'):
            if os.path.isdir('SlidesInfo/' + name):
                s = read(self.rootdir + "/SlidesInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\title{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                checkbox = QtWidgets.QCheckBox(titre)
                path = 'SlidesInfo/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formSlidesInfo.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateTDInfo(self):
        if not os.path.exists('TDInfo'):
            return
        i = 0
        for name in os.listdir('TDInfo'):
            if os.path.isdir('TDInfo/' + name):
                s = read(self.rootdir + "/TDInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formTDInfo.addWidget(QtWidgets.QLabel(titre), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'TDInfo/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTDInfo.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'TDInfo/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTDInfo.addWidget(checkbox, i, 2)
                i += 1

    def populateTPInfo(self):
        if not os.path.exists('TPInfo'):
            return
        i = 0
        for name in os.listdir('TPInfo'):
            if os.path.isdir('TPInfo/' + name):
                s = read(self.rootdir + "/TPInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretp{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.formTPInfo.addWidget(QtWidgets.QLabel(titre), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'TPInfo/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTPInfo.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'TPInfo/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formTPInfo.addWidget(checkbox, i, 2)
                i += 1

    def populateDSInfo(self):
        if not os.path.exists('DSInfo'):
            return
        i = 0
        for name in os.listdir('DSInfo'):
            if 'DSInfo' in name and os.path.isdir('DSInfo/' + name):
                self.formDSInfo.addWidget(QtWidgets.QLabel(name), i, 0)
                checkbox = QtWidgets.QCheckBox('Enoncé')
                path = 'DSInfo/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDSInfo.addWidget(checkbox, i, 1)
                checkbox = QtWidgets.QCheckBox('Corrigé')
                path = 'DSInfo/' + name + '/' + name + '_corrige.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formDSInfo.addWidget(checkbox, i, 2)
                i += 1

    def populateADS(self):
        presentations = self.html('div#presentations')
        i = 0
        for li in presentations('li'):
            info = re.search(r"(.*?)<br.*?>(.*?) *(\d{2})/(\d{2})/(\d{4}).*?<br.*?>(.*)", pq(li).html(), re.DOTALL)
            file = os.path.basename(pq(li)('a').attr("href"))
            titre = QtWidgets.QLineEdit(info.group(6).strip())
            titre.home(True)
            titre.deselect()
            self.formADS.addWidget(titre, i, 0)
            eleve = QtWidgets.QLineEdit(info.group(2).strip())
            eleve.home(True)
            eleve.deselect()
            self.formADS.addWidget(eleve, i, 1)
            date = QtWidgets.QDateTimeEdit(
                QtCore.QDate(int(info.group(5).strip()), int(info.group(4).strip()), int(info.group(3).strip())))
            date.setCalendarPopup(True)
            self.formADS.addWidget(date, i, 2)
            files = QtWidgets.QComboBox()
            files.addItems(os.listdir('ADS'))
            files.setCurrentIndex(files.findText(file))
            self.formADS.addWidget(files, i, 3)
            self.formADS.addWidget(QtWidgets.QCheckBox(), i, 4)
            i += 1

    def populateFormulaires(self):
        i = 0
        for name in os.listdir('Formulaires'):
            if os.path.isdir('Formulaires/' + name):
                s = read(self.rootdir + "/Formulaires/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titreformulaire{(.*?)}", s, re.DOTALL).group(1)
                checkbox = QtWidgets.QCheckBox(titre)
                path = 'Formulaires/' + name + '/' + name + '.pdf'
                checkbox.setObjectName(path)
                if self.html('a[href="' + path + '"]'):
                    checkbox.setChecked(True)
                if not os.path.exists(path):
                    checkbox.setDisabled(True)
                self.formFormulaires.addWidget(checkbox, i / 4, i % 4)
                i += 1

    def populateAnimations(self):
        animations = self.html('div#animations')
        fs = QtWidgets.QFileSystemModel()
        fs.setRootPath(self.rootdir + "/Animations")
        i = 0
        for li in animations('li'):
            titre = QtWidgets.QLineEdit(pq(li)('p').text())
            titre.home(True)
            titre.deselect()
            self.formAnimations.addWidget(titre, i, 0)
            animtype = pq(li)('img').attr("class")
            combobox = QtWidgets.QComboBox()
            combobox.addItems(["GeoGebra", "Flash", "JavaScript", "Sage"])
            combobox.setCurrentIndex({'geogebra': 0, 'flash': 1, 'javascript': 2, 'sage': 3}.get(animtype, 0))
            self.formAnimations.addWidget(combobox, i, 1)
            lineedit = QtWidgets.QLineEdit()
            completer = QtWidgets.QCompleter()
            completer.setModel(fs)
            completer.setCompletionPrefix(self.rootdir + "/Animations/")
            file = pq(li)('a').attr("href")
            lineedit.setText(self.rootdir + "/" + file)
            lineedit.setCompleter(completer)
            self.formAnimations.addWidget(lineedit, i, 2)
            self.formAnimations.addWidget(QtWidgets.QCheckBox(), i, 3)
            i += 1

    def updateDS(self):
        ds = self.html('div#ds')
        ul = ds('ul')
        ul.empty()
        if self.formDS.count() == 0:
            return
        for i in range(self.formDS.rowCount()):
            if self.formDS.itemAtPosition(i, 1).widget().isChecked() or self.formDS.itemAtPosition(i,
                                                                                                   2).widget().isChecked():
                number = self.formDS.itemAtPosition(i, 1).widget().objectName()
                number = os.path.splitext(os.path.basename(number))[0]
                number = number.replace('DS', '').lstrip('0')
                li = pq('<li>').html("Devoir n°" + number)
                li.append(pq('<br>'))
                if self.formDS.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formDS.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                if self.formDS.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formDS.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateDM(self):
        dm = self.html('div#dm')
        ul = dm('ul')
        ul.empty()
        if self.formDM.count() == 0:
            return
        for i in range(self.formDM.rowCount()):
            if self.formDM.itemAtPosition(i, 1).widget().isChecked() or self.formDM.itemAtPosition(i,
                                                                                                   2).widget().isChecked():
                number = self.formDM.itemAtPosition(i, 1).widget().objectName()
                number = os.path.splitext(os.path.basename(number))[0]
                number = number.replace('DM', '').lstrip('0')
                li = pq('<li>').html("Devoir n°" + number)
                li.append(pq('<br>'))
                if self.formDM.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formDM.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                if self.formDM.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formDM.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateColles(self):
        colles = self.html('div#colles')
        ul = colles('ul')
        ul.empty()
        for i in range(self.formColles.count()):
            if (self.formColles.itemAt(i).widget().isChecked()):
                path = self.formColles.itemAt(i).widget().objectName()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + "Semaine " + str(i + 1) + '</p>')
                ul.append(li)

    def updateCours(self):
        notescours = self.html('div#notescours')
        ul = notescours('ul')
        ul.empty()
        for i in range(self.formCours.count()):
            if (self.formCours.itemAt(i).widget().isChecked()):
                name = self.formCours.itemAt(i).widget().text()
                path = self.formCours.itemAt(i).widget().objectName()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + name + '</p>')
                li.append(pq('<br>'))
                ul.append(li)

    def updateInterros(self):
        interros = self.html('div#interros')
        ul = interros('ul')
        ul.empty()
        for i in range(self.formInterros.count()):
            if (self.formInterros.itemAt(i).widget().isChecked()):
                path = self.formInterros.itemAt(i).widget().objectName()
                number = os.path.splitext(os.path.basename(path))[0]
                number = number.replace('Interro', '').lstrip('0')
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + "Interro n°" + number + '</p>')
                li.append(pq('<br>'))
                ul.append(li)

    def updateTD(self):
        sujetstd = self.html('div#td')
        ul = sujetstd('ul')
        ul.empty()
        if self.formTD.count() == 0:
            return
        for i in range(self.formTD.rowCount()):
            if self.formTD.itemAtPosition(i, 1).widget().isChecked() or self.formTD.itemAtPosition(i,
                                                                                                   2).widget().isChecked():
                name = self.formTD.itemAtPosition(i, 0).widget().text()
                li = pq('<li>').html('<p>' + name + '</p>')
                li.append(pq('<br>'))
                if self.formTD.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formTD.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append('<br>')
                if self.formTD.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formTD.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateInfo(self):
        info = self.html('div#coursinfo')
        ul = info('ul')
        ul.empty()
        for i in range(self.formInfo.count()):
            if (self.formInfo.itemAt(i).widget().isChecked()):
                name = self.formInfo.itemAt(i).widget().text()
                path = self.formInfo.itemAt(i).widget().objectName()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + name + '</p>')
                li.append(pq('<br>'))
                ul.append(li)

    def updateSlidesInfo(self):
        info = self.html('div#slidesinfo')
        ul = info('ul')
        ul.empty()
        for i in range(self.formSlidesInfo.count()):
            if (self.formSlidesInfo.itemAt(i).widget().isChecked()):
                name = self.formSlidesInfo.itemAt(i).widget().text()
                path = self.formSlidesInfo.itemAt(i).widget().objectName()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + name + '</p>')
                li.append(pq('<br>'))
                ul.append(li)

    def updateTDInfo(self):
        sujetstdinfo = self.html('div#tdinfo')
        ul = sujetstdinfo('ul')
        ul.empty()
        if self.formTDInfo.count() == 0:
            return
        for i in range(self.formTDInfo.rowCount()):
            if self.formTDInfo.itemAtPosition(i, 1).widget().isChecked() or self.formTDInfo.itemAtPosition(i,
                                                                                                           2).widget().isChecked():
                name = self.formTDInfo.itemAtPosition(i, 0).widget().text()
                li = pq('<li>').html('<p>' + name + '</p>')
                li.append(pq('<br>'))
                if self.formTDInfo.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formTDInfo.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append('<br>')
                if self.formTDInfo.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formTDInfo.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateTPInfo(self):
        sujetstpinfo = self.html('div#tpinfo')
        ul = sujetstpinfo('ul')
        ul.empty()
        if self.formTPInfo.count() == 0:
            return
        for i in range(self.formTPInfo.rowCount()):
            if self.formTPInfo.itemAtPosition(i, 1).widget().isChecked() or self.formTPInfo.itemAtPosition(i,
                                                                                                           2).widget().isChecked():
                name = self.formTPInfo.itemAtPosition(i, 0).widget().text()
                li = pq('<li>').html('<p>' + name + '</p>')
                li.append(pq('<br>'))
                if self.formTPInfo.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formTPInfo.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append('<br>')
                if self.formTPInfo.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formTPInfo.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateDSInfo(self):
        dsinfo = self.html('div#dsinfo')
        ul = dsinfo('ul')
        ul.empty()
        if self.formDSInfo.count() == 0:
            return
        for i in range(self.formDSInfo.rowCount()):
            if self.formDSInfo.itemAtPosition(i, 1).widget().isChecked() or self.formDSInfo.itemAtPosition(i,
                                                                                                           2).widget().isChecked():
                number = self.formDSInfo.itemAtPosition(i, 1).widget().objectName()
                number = os.path.splitext(os.path.basename(number))[0]
                number = number.replace('DSInfo', '').lstrip('0')
                li = pq('<li>').html("Devoir n°" + number)
                li.append(pq('<br>'))
                if self.formDSInfo.itemAtPosition(i, 1).widget().isChecked():
                    path = self.formDSInfo.itemAtPosition(i, 1).widget().objectName()
                    li.append(pq('<a>').html('Enoncé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                if self.formDSInfo.itemAtPosition(i, 2).widget().isChecked():
                    path = self.formDSInfo.itemAtPosition(i, 2).widget().objectName()
                    li.append(pq('<a>').html('Corrigé').attr(href=path).append('<img src="" alt="" class="smallpdf"/>'))
                li.append(pq('<br>'))
                ul.append(li)

    def updateADS(self):
        presentations = self.html('div#presentations')
        ul = presentations('ul')
        ul.empty()
        if self.formADS.count() == 0:
            return
        for i in range(self.formADS.rowCount()):
            try:
                titre = self.formADS.itemAtPosition(i, 0).widget().text()
                eleve = self.formADS.itemAtPosition(i, 1).widget().text()
                date = self.formADS.itemAtPosition(i, 2).widget().date().toString("dd/MM/yyyy")
                file = 'ADS/' + self.formADS.itemAtPosition(i, 3).widget().currentText()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=file).append('<img src="" alt="" class="bigpdf">'))
                li.append(pq('<br>'))
                li.append(eleve + " " + date)
                li.append(pq('<br>'))
                li.append(titre)
                ul.append(li)
            except:
                pass

    def updateFormulaires(self):
        formulaires = self.html('div#formulaires')
        ul = formulaires('ul')
        ul.empty()
        for i in range(self.formFormulaires.count()):
            if (self.formFormulaires.itemAt(i).widget().isChecked()):
                path = self.formFormulaires.itemAt(i).widget().objectName()
                li = pq('<li>')
                li.append(pq('<a>').attr(href=path).append(pq('<img src="" alt="" class="bigpdf">')))
                li.append(pq('<br>'))
                li.append('<p>' + self.formFormulaires.itemAt(i).widget().text() + '</p>')
                li.append(pq('<br>'))
                ul.append(li)

    def updateAnimations(self):
        animations = self.html('div#animations')
        ul = animations('ul')
        ul.empty()
        if self.formAnimations.count() == 0:
            return
        for i in range(self.formAnimations.rowCount()):
            try:
                titre = self.formAnimations.itemAtPosition(i, 0).widget().text()
                animtype = self.formAnimations.itemAtPosition(i, 1).widget().currentText().lower()
                file = QtCore.QDir.fromNativeSeparators(
                    os.path.relpath(self.formAnimations.itemAtPosition(i, 2).widget().text()))
                li = pq('<li>')
                li.append(pq('<a>').attr(href=file).append('<img src="" alt="" class="' + animtype + '">'))
                li.append(pq('<br>'))
                li.append(pq('<p>').html(titre))
                ul.append(li)
            except:
                pass

    @QtCore.pyqtSlot()
    def on_removeADSButton_clicked(self):
        for i in range(self.formADS.rowCount()):
            try:
                if self.formADS.itemAtPosition(i, 4).widget().isChecked():
                    for j in range(self.formADS.columnCount()):
                        widget = self.formADS.itemAtPosition(i, j).widget()
                        self.formADS.removeWidget(widget)
                        widget.hide()
                        del widget
                        self.formADS.update()
            except:
                pass

    @QtCore.pyqtSlot()
    def on_addADSButton_clicked(self):
        n = self.formADS.rowCount()
        self.formADS.addWidget(QtWidgets.QLineEdit(), n, 0)
        self.formADS.addWidget(QtWidgets.QLineEdit(), n, 1)
        date = QtWidgets.QDateTimeEdit(QtCore.QDate.currentDate())
        date.setCalendarPopup(True)
        self.formADS.addWidget(date, n, 2)
        files = QtWidgets.QComboBox()
        files.addItems(os.listdir('ADS'))
        files.setCurrentIndex(-1)
        self.formADS.addWidget(files, n, 3)
        self.formADS.addWidget(QtWidgets.QCheckBox(), n, 4)

    @QtCore.pyqtSlot()
    def on_removeAnimationsButton_clicked(self):
        for i in range(self.formAnimations.rowCount()):
            try:
                if self.formAnimations.itemAtPosition(i, 3).widget().isChecked():
                    for j in range(self.formAnimations.columnCount()):
                        widget = self.formAnimations.itemAtPosition(i, j).widget()
                        self.formAnimations.removeWidget(widget)
                        widget.hide()
                        del widget
                        self.formAnimations.update()
            except:
                pass

    @QtCore.pyqtSlot()
    def on_addAnimationsButton_clicked(self):
        n = self.formAnimations.rowCount()
        self.formAnimations.addWidget(QtWidgets.QLineEdit(), n, 0)
        combobox = QtWidgets.QComboBox()
        combobox.addItems(["GeoGebra", "Flash", "JavaScript", "Sage"])
        combobox.setCurrentIndex(-1)
        self.formAnimations.addWidget(combobox, n, 1)
        fs = QtWidgets.QFileSystemModel()
        fs.setRootPath(self.rootdir + "/Animations")
        lineedit = QtWidgets.QLineEdit()
        completer = QtWidgets.QCompleter()
        completer.setModel(fs)
        completer.setCompletionPrefix(self.rootdir + "/Animations/")
        lineedit.setCompleter(completer)
        lineedit.setText(self.rootdir + "/Animations/")
        self.formAnimations.addWidget(lineedit, n, 2)
        self.formAnimations.addWidget(QtWidgets.QCheckBox(), n, 3)

    @QtCore.pyqtSlot()
    def on_transferButton_clicked(self):
        self.message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Transfert", "Transfert FTP",
                                             QtWidgets.QMessageBox.Cancel)
        self.message.buttonClicked.connect(self.cancelTransfer)
        # spacer = QtWidgets.QSpacerItem(500, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # l = self.message.layout()
        # l.addItem(spacer, l.rowCount(), 0, 1, l.columnCount())
        self.detailedMessage = "Début du transfert"
        self.message.setDetailedText(self.detailedMessage)
        self.message.show()
        self.update()
        self.writeLocalHTML()
        self.transfer()

    def on_saveButton_clicked(self):
        self.message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Sauvegarde", "Sauvegarde",
                                             QtWidgets.QMessageBox.Cancel)
        self.message.setInformativeText("Sauvegarde en cours")
        self.message.show()
        self.update()
        self.writeLocalHTML()
        self.message.setInformativeText("Sauvegarde terminée")

    def on_reloadButton_clicked(self):
        self.load()

    def cancelTransfer(self):
        self.ftp.abort()
        self.ftp.close()

    def updateMessage(self, mess):
        self.detailedMessage = mess + '\n' + self.detailedMessage
        self.message.setDetailedText(self.detailedMessage)


class TransferThread(QtCore.QThread):
    message = QtCore.pyqtSignal(str)

    def __init__(self, localFileList, parent=None):
        super(TransferThread, self).__init__(parent)
        self.localFileList = localFileList

    def run(self):
        # with FTPHost("127.0.0.1", "lgarcin", "") as ftp:
        with FTPHost("ftpperso.free.fr", "laurentb.garcin", "xRSGeOeu") as ftp:
            for file in self.localFileList:
                path = os.path.dirname(file)
                if not ftp.path.exists(path):
                    ftp.makedirs(path)
                    self.message.emit("Création du répertoire " + path)
                rate = True
                while rate:
                    try:
                        if ftp.upload_if_newer(file, file):
                            self.message.emit("Création du fichier " + file)
                        else:
                            # self.message.emit("Passage du fichier " + file)
                            pass
                        rate = False
                    except:
                        self.message.emit("Création du fichier " + file + " abandonnée")
                        sleep(1)
            for dirpath, dirnames, filenames in ftp.walk('/', topdown=False):
                for file in filenames:
                    fullpath = QtCore.QDir.fromNativeSeparators(os.path.join(dirpath, file))
                    if fullpath[1:] not in self.localFileList:
                        ftp.remove(fullpath)
                        self.message.emit("Destruction du fichier " + fullpath)
                for d in dirnames:
                    fullpath = QtCore.QDir.fromNativeSeparators(os.path.join(dirpath, d))
                    if not ftp.listdir(fullpath):
                        ftp.rmdir(fullpath)
                        self.message.emit("Destruction du répertoire " + fullpath)

        self.message.emit("Transfert terminé")


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtWidgets.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
