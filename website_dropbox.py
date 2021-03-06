'''
Created on 27 nov. 2014

@author: Laurent
'''

# Remplacer les os par des QDir, QFile
# Remplacer les re par des QRegExp ou QRegularExpression (pyqt5)


import sys, locale, os, re, json, io
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from dropbox.client import DropboxClient
from datetime import datetime
from dateutil import parser

scriptdir = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(os.path.join(scriptdir, 'website_dropbox.ui'))


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


class FileWidget(QtWidgets.QWidget):
    def __init__(self, fw, parent=None):
        super(FileWidget, self).__init__(parent)
        self.transferInfo = self.parent().transferInfo
        self.fw = fw
        nomWidget = QtWidgets.QLabel(fw['type'])
        self.fileChooserWidget = QtWidgets.QPushButton()
        if 'path' in self.fw:
            self.fileChooserWidget.setText(fw['path'])
            self.transferInfo.append(self.fw)
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
        self.fileChooserWidget.clicked.connect(self.selectFile)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(self.fileChooserWidget)

    def selectFile(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Choisir un fichier...')
        if fname:
            self.fileChooserWidget.setText(fname)
            if self.fw not in self.transferInfo:
                self.transferInfo.append(self.fw)
            self.fw.update({'path': fname})
        else:
            self.fileChooserWidget.setText('Choisir un fichier...')
            if self.fw in self.transferInfo:
                self.transferInfo.remove(self.fw)


class EnonceCorrigeWidget(QtWidgets.QWidget):
    def __init__(self, ec, parent=None):
        super(EnonceCorrigeWidget, self).__init__(parent)
        self.transferInfo = self.parent().transferInfo
        self.current = ec
        self.transferInfo.append(ec)
        self.enonce = ec['enoncepath']
        self.corrige = ec['corrigepath']
        nomWidget = QtWidgets.QLabel(ec['nom'])

        self.enonceWidget = QtWidgets.QCheckBox('Enoncé')
        self.corrigeWidget = QtWidgets.QCheckBox('Corrigé')
        self.enonceWidget.stateChanged.connect(self.updateInfo)
        self.corrigeWidget.stateChanged.connect(self.updateInfo)

        if self.enonce in [e['enoncepath'] for e in self.parent().remoteInfo if 'enoncepath' in e]:
            self.enonceWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(os.path.join(self.parent().localDir, self.enonce)):
            self.enonceWidget.setDisabled(True)

        if self.corrige in [c['corrigepath'] for c in self.parent().remoteInfo if 'corrigepath' in c]:
            self.corrigeWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(os.path.join(self.parent().localDir, self.corrige)):
            self.corrigeWidget.setDisabled(True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(self.enonceWidget)
        layout.addWidget(self.corrigeWidget)

    def updateInfo(self):
        self.transferInfo.remove(self.current)
        if self.enonceWidget.isChecked():
            self.current['enoncepath'] = self.enonce
        else:
            self.current.pop('enoncepath', None)
        if self.corrigeWidget.isChecked():
            self.current['corrigepath'] = self.corrige
        else:
            self.current.pop('corrigepath', None)
        if 'enoncepath' in self.current or 'corrigepath' in self.current:
            self.transferInfo.append(self.current)


class CoursWidget(QtWidgets.QWidget):
    def __init__(self, cours, parent=None):
        super(CoursWidget, self).__init__(parent)
        transferInfo = self.parent().transferInfo
        coursWidget = QtWidgets.QCheckBox(cours['nom'])
        coursWidget.stateChanged.connect(
            lambda state: transferInfo.append(cours) if state == QtCore.Qt.Checked else transferInfo.remove(cours))
        if cours in self.parent().remoteInfo:
            coursWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(os.path.join(self.parent().localDir, cours['path'])):
            coursWidget.setDisabled(True)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(coursWidget)


class AnimationWidget(QtWidgets.QWidget):
    def __init__(self, animation, parent=None):
        super(AnimationWidget, self).__init__(parent)
        transferInfo = self.parent().transferInfo
        transferInfo.append(animation)
        self.destroyed.connect(lambda _: transferInfo.remove(animation))
        nomWidget = QtWidgets.QLineEdit(animation['nom'])
        nomWidget.home(True)
        nomWidget.deselect()
        nomWidget.textChanged.connect(lambda text, animation=animation: animation.update({'nom': text}))
        lienWidget = QtWidgets.QLineEdit(animation['lien'])
        lienWidget.home(True)
        lienWidget.deselect()
        lienWidget.textChanged.connect(lambda text, animation=animation: animation.update({'lien': text}))
        iconWidget = QtWidgets.QComboBox()
        icons = ["GeoGebra", "Flash", "JavaScript", "Python"]
        iconWidget.addItems(icons)
        iconWidget.setCurrentIndex(iconWidget.findText(animation['icon']))
        iconWidget.currentIndexChanged.connect(lambda index: animation.update({'icon': iconWidget.currentText()}))
        self.check = QtWidgets.QCheckBox()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(lienWidget)
        layout.addWidget(iconWidget)
        layout.addWidget(self.check)


class ADSWidget(QtWidgets.QWidget):
    def __init__(self, ads, parent=None):
        super(ADSWidget, self).__init__(parent)
        transferInfo = self.parent().transferInfo
        transferInfo.append(ads)
        self.destroyed.connect(lambda _: transferInfo.remove(ads))
        nomWidget = QtWidgets.QLineEdit(ads['nom'])
        nomWidget.home(True)
        nomWidget.deselect()
        nomWidget.textChanged.connect(lambda text, ads=ads: ads.update({'nom': text}))
        eleveWidget = QtWidgets.QLineEdit(ads['eleve'])
        eleveWidget.home(True)
        eleveWidget.deselect()
        eleveWidget.textChanged.connect(lambda text, ads=ads: ads.update({'eleve': text}))
        dateWidget = QtWidgets.QDateTimeEdit(QtCore.QDate.fromString(ads['date'], format=QtCore.Qt.DefaultLocaleLongDate))
        dateWidget.setCalendarPopup(True)
        dateWidget.dateChanged.connect(
            lambda date, ads=ads: ads.update({'date': date.toString(QtCore.Qt.DefaultLocaleLongDate)}))
        fileWidget = QtWidgets.QComboBox()
        fileWidget.addItems(os.listdir('ADS'))
        fileWidget.setCurrentIndex(fileWidget.findText(ads['path']))
        fileWidget.currentIndexChanged.connect(lambda text, ads=ads: ads.update({'path': text}))
        self.check = QtWidgets.QCheckBox()
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(eleveWidget)
        layout.addWidget(dateWidget)
        layout.addWidget(fileWidget)
        layout.addWidget(self.check)


class WebSite(form_class, base_class):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        self.setupUi(self)
        self.addADSButton.setIcon(QtGui.QIcon(os.path.join(scriptdir, "images/plus_32.ico")))
        self.removeADSButton.setIcon(QtGui.QIcon(os.path.join(scriptdir, "images/delete_32.ico")))
        self.addAnimationsButton.setIcon(QtGui.QIcon(os.path.join(scriptdir, "images/plus_32.ico")))
        self.removeAnimationsButton.setIcon(QtGui.QIcon(os.path.join(scriptdir, "images/delete_32.ico")))
        self.transferButton.setIcon(QtGui.QIcon(os.path.join(scriptdir, "images/ftp_64.png")))
        self.localDir = "F:/Documents/Enseignement/Corot/"
        self.remoteDir = "F:/Documents/Enseignement/Test/"
        os.chdir(self.localDir)
        self.transferInfo = []
        self.getLocalInfo()
        self.client = DropboxClient('gS7qI3Fbn2AAAAAAAAAAFqW6G3O73LJxk9yZutwCO5Q2RT-bbYVdbbz-EskRLiQj')
        self.getRemoteInfo()
        self.fillForms()

    def getRemoteInfo(self):
        try:
            with self.client.get_file('data.json') as f:
                self.remoteInfo = json.loads(f.read().decode('utf-8'))
        except:
            self.remoteInfo = []

    def getLocalInfo(self):
        self.localInfo = []
        for name in sorted(os.listdir('DS')):
            if 'DS' in name and os.path.isdir('DS/' + name):
                self.localInfo.append({'nom': name, 'type': 'DS', 'enoncepath': 'DS/' + name + '/' + name + '.pdf',
                                       'corrigepath': 'DS/' + name + '/' + name + '_corrige.pdf'})

        for name in sorted(os.listdir('DM')):
            if 'DM' in name and os.path.isdir('DM/' + name):
                self.localInfo.append({'nom': name, 'type': 'DM', 'enoncepath': 'DM/' + name + '/' + name + '.pdf',
                                       'corrigepath': 'DM/' + name + '/' + name + '_corrige.pdf'})

        for name in sorted(os.listdir('Cours')):
            if os.path.isdir('Cours/' + name):
                s = read(self.localDir + "Cours/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom': titre, 'type': 'cours', 'path': 'Cours/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('Formulaires')):
            if os.path.isdir('Formulaires/' + name):
                s = read(self.localDir + "Formulaires/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titreformulaire{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append(
                    {'nom': titre, 'type': 'formulaire', 'path': 'Formulaires/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('Colles')):
            if 'ProgColles' in name and os.path.isdir('Colles/' + name):
                self.localInfo.append({'nom': name, 'type': 'colle', 'path': 'Colles/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('Interros')):
            if 'Interro' in name and os.path.isdir('Interros/' + name):
                self.localInfo.append(
                    {'nom': name, 'type': 'interro', 'path': 'Interros/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('TD')):
            if os.path.isdir('TD/' + name):
                s = read(self.localDir + "TD/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom': titre, 'type': 'TD', 'enoncepath': 'TD/' + name + '/' + name + '.pdf',
                                       'corrigepath': 'TD/' + name + '/' + name + '_corrige.pdf'})

        return

        for name in sorted(os.listdir('Info')):
            if os.path.isdir('Info/' + name):
                s = read(self.localDir + "Info/" + name + "/" + name + ".tex");
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom': titre, 'type': 'info', 'path': 'Info/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('SlidesInfo')):
            if os.path.isdir('SlidesInfo/' + name):
                s = read(self.localDir + "SlidesInfo/" + name + "/" + name + ".tex");
                titre = re.search(r"\\title{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append(
                    {'nom': titre, 'type': 'slidesinfo', 'path': 'SlidesInfo/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('TDInfo')):
            if os.path.isdir('TDInfo/' + name):
                s = read(self.localDir + "TDInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append(
                    {'nom': titre, 'type': 'TDinfo', 'enoncepath': 'TDInfo/' + name + '/' + name + '.pdf',
                     'corrigepath': 'TDInfo/' + name + '/' + name + '_corrige.pdf'})

        for name in sorted(os.listdir('TPInfo')):
            if os.path.isdir('TPInfo/' + name):
                s = read(self.localDir + "TPInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append(
                    {'nom': titre, 'type': 'TPinfo', 'enoncepath': 'TPInfo/' + name + '/' + name + '.pdf',
                     'corrigepath': 'TPInfo/' + name + '/' + name + '_corrige.pdf'})

        for name in sorted(os.listdir('DSInfo')):
            if 'DSInfo' in name and os.path.isdir('DSInfo/' + name):
                self.localInfo.append(
                    {'nom': name, 'type': 'DSinfo', 'enoncepath': 'DSInfo/' + name + '/' + name + '.pdf',
                     'corrigepath': 'DSInfo/' + name + '/' + name + '_corrige.pdf'})

    def clearForms(self):
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

    def fillForms(self):
        n = next((item for item in self.remoteInfo if item['type'] == 'Colloscope'), {'type': 'Colloscope'})
        self.formVieclasse.addWidget(FileWidget(n.copy(), self))
        n = next((item for item in self.remoteInfo if item['type'] == 'Emploi du temps'), {'type': 'Emploi du temps'})
        self.formVieclasse.addWidget(FileWidget(n.copy(), self))
        n = next((item for item in self.remoteInfo if item['type'] == 'Planning des DS'), {'type': 'Planning des DS'})
        self.formVieclasse.addWidget(FileWidget(n.copy(), self))
        n = next((item for item in self.remoteInfo if item['type'] == 'Notes premier semestre'),
                 {'type': 'Notes premier semestre'})
        self.formVieclasse.addWidget(FileWidget(n.copy(), self))
        n = next((item for item in self.remoteInfo if item['type'] == 'Notes second semestre'),
                 {'type': 'Notes second semestre'})
        self.formVieclasse.addWidget(FileWidget(n.copy(), self))

        for ds in [e for e in self.localInfo if e['type'] == 'DS']:
            self.formDS.addWidget(EnonceCorrigeWidget(ds, self))

        for dm in [e for e in self.localInfo if e['type'] == 'DM']:
            self.formDM.addWidget(EnonceCorrigeWidget(dm, self))

        for i, cours in enumerate([e for e in self.localInfo if e['type'] == 'cours']):
            self.formCours.addWidget(CoursWidget(cours, self), i / 4, i % 4)

        for i, formulaire in enumerate([e for e in self.localInfo if e['type'] == 'formulaire']):
            self.formFormulaires.addWidget(CoursWidget(formulaire, self), i / 4, i % 4)

        for i, colle in enumerate([e for e in self.localInfo if e['type'] == 'colle']):
            self.formColles.addWidget(CoursWidget(colle, self), i / 4, i % 4)

        for i, interro in enumerate([e for e in self.localInfo if e['type'] == 'interro']):
            self.formInterros.addWidget(CoursWidget(interro, self), i / 4, i % 4)

        for td in [e for e in self.localInfo if e['type'] == 'TD']:
            self.formTD.addWidget(EnonceCorrigeWidget(td, self))

        for i, info in enumerate([e for e in self.localInfo if e['type'] == 'info']):
            self.formInfo.addWidget(CoursWidget(info, self), i / 4, i % 4)

        for i, slidesinfo in enumerate([e for e in self.localInfo if e['type'] == 'slidesinfo']):
            self.formSlidesInfo.addWidget(CoursWidget(slidesinfo), i / 4, i % 4)

        for tdinfo in [e for e in self.localInfo if e['type'] == 'TDinfo']:
            self.formTDInfo.addWidget(EnonceCorrigeWidget(tdinfo, self))

        for tpinfo in [e for e in self.localInfo if e['type'] == 'TPinfo']:
            self.formTPInfo.addWidget(EnonceCorrigeWidget(tpinfo, self))

        for dsinfo in [e for e in self.localInfo if e['type'] == 'DSinfo']:
            self.formDSInfo.addWidget(EnonceCorrigeWidget(dsinfo, self))

        for animation in [e for e in self.remoteInfo if e['type'] == 'animation']:
            self.formAnimations.addWidget(AnimationWidget(animation, self))

    def updateMessage(self, mess):
        self.detailedMessage += mess + '\n'
        self.message.setDetailedText(self.detailedMessage)

    @QtCore.pyqtSlot()
    def on_addADSButton_clicked(self):
        ads = {'nom': '', 'eleve': '', 'type': 'ads', 'date': '', 'path': ''}
        self.formADS.addWidget(ADSWidget(ads, self))

    @QtCore.pyqtSlot()
    def on_removeADSButton_clicked(self):
        for widget in self.findChildren(ADSWidget):
            if widget.check.isChecked():
                self.formADS.removeWidget(widget)
                widget.deleteLater()
                self.formADS.update()

    @QtCore.pyqtSlot()
    def on_addAnimationsButton_clicked(self):
        animation = {'nom': '', 'lien': '', 'type': 'animation', 'icon': ''}
        self.formAnimations.addWidget(AnimationWidget(animation, self))

    @QtCore.pyqtSlot()
    def on_removeAnimationsButton_clicked(self):
        for widget in self.findChildren(AnimationWidget):
            if widget.check.isChecked():
                self.formAnimations.removeWidget(widget)
                widget.deleteLater()
                self.formAnimations.update()

    @QtCore.pyqtSlot()
    def on_transferButton_clicked(self):
        self.message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Transfert", "Transfert",
                                         QtWidgets.QMessageBox.Cancel)
        spacer = QtWidgets.QSpacerItem(500, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        l = self.message.layout()
        l.addItem(spacer, l.rowCount(), 0, 1, l.columnCount())
        self.detailedMessage = 'Début du transfert\n'
        self.message.setDetailedText(self.detailedMessage)
        self.message.show()

        transferFiles = [e['path'] for e in self.transferInfo if 'path' in e.keys()]
        transferFiles += [e['enoncepath'] for e in self.transferInfo if 'enoncepath' in e.keys()]
        transferFiles += [e['corrigepath'] for e in self.transferInfo if 'corrigepath' in e.keys()]

        remoteFiles = [e['path'] for e in self.remoteInfo if 'path' in e.keys()]
        remoteFiles += [e['enoncepath'] for e in self.remoteInfo if 'enoncepath' in e.keys()]
        remoteFiles += [e['corrigepath'] for e in self.remoteInfo if 'corrigepath' in e.keys()]

        copyFiles = [f for f in transferFiles if f not in remoteFiles]
        updateFiles = [f for f in transferFiles if f in remoteFiles]
        deleteFiles = [f for f in remoteFiles if f not in transferFiles]

        self.thread = TransferThread(self.client, self.localDir, copyFiles, updateFiles, deleteFiles, self.transferInfo)
        self.thread.start()
        self.thread.message.connect(self.updateMessage)


class TransferThread(QtCore.QThread):
    message = QtCore.pyqtSignal(str)

    def __init__(self, client, localDir, copyFiles, updateFiles, deleteFiles, transferInfo, parent=None):
        super(TransferThread, self).__init__(parent)
        self.client = client
        self.localDir = localDir
        self.copyFiles = copyFiles
        self.updateFiles = updateFiles
        self.deleteFiles = deleteFiles
        self.transferInfo = transferInfo

    def run(self):
        for f in self.copyFiles:
            with open(os.path.join(self.localDir, f), 'rb') as fd:
                self.client.put_file(os.path.basename(f), fd, overwrite=True)
                self.message.emit("Copie de " + os.path.basename(f))

        for f in self.updateFiles:
            localFile = os.path.join(self.localDir, f)
            remoteFile = os.path.basename(f)
            localTime = os.path.getmtime(localFile)
            remoteTime = self.client.metadata(remoteFile)['modified']
            if datetime.fromtimestamp(localTime) > parser.parse(remoteTime, ignoretz=True):
                with open(localFile, 'rb') as fd:
                    self.client.put_file(os.path.basename(f), fd, overwrite=True)
                    self.message.emit("Mise à jour de " + os.path.basename(f))

        for f in self.deleteFiles:
            self.client.file_delete(os.path.basename(f))
            self.message.emit("Destruction de " + os.path.basename(f))

        f = io.StringIO()
        json.dump(self.transferInfo, f)
        self.client.put_file("data.json", f, overwrite=True)
        self.message.emit("Copie du fichier JSON")

        self.message.emit("Transfert terminé")


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtWidgets.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
