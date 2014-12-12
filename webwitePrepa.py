'''
Created on 27 nov. 2014

@author: Laurent
'''

# Remplacer les os par des QDir, QFile

import sys, locale, os, re, json
from PyQt4 import QtGui, QtCore, uic

scriptdir = os.path.dirname(__file__)
form_class, base_class = uic.loadUiType(scriptdir + '/websitePrepa.ui')

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

    
class EnonceCorrigeWidget(QtGui.QWidget):
    def __init__(self, enonce, corrige, parent=None):
        super(EnonceCorrigeWidget, self).__init__(parent)
        transferInfo=self.parent().transferInfo
        nomWidget = QtGui.QLabel(enonce['nom'])
        enonceWidget = QtGui.QCheckBox('Enoncé')
        enonceWidget.stateChanged.connect(lambda state: transferInfo.append(enonce) if state == QtCore.Qt.Checked else transferInfo.remove(enonce))
        if enonce in self.parent().remoteInfo:
            enonceWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(self.parent().localdir + enonce['path']):
            print(self.parent().localdir + enonce['path'])
            enonceWidget.setDisabled(True)
        corrigeWidget = QtGui.QCheckBox('Corrigé')
        corrigeWidget.stateChanged.connect(lambda state: transferInfo.append(corrige) if state == QtCore.Qt.Checked else transferInfo.remove(corrige))
        if corrige in self.parent().remoteInfo:
            corrigeWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(self.parent().localdir + corrige['path']):
            corrigeWidget.setDisabled(True)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(enonceWidget)
        layout.addWidget(corrigeWidget)

class CoursWidget(QtGui.QWidget):
    def __init__(self, cours, parent=None):
        super(CoursWidget, self).__init__(parent)
        transferInfo=self.parent().transferInfo
        coursWidget = QtGui.QCheckBox(cours['nom'])
        coursWidget.stateChanged.connect(lambda state: transferInfo.append(cours) if state == QtCore.Qt.Checked else transferInfo.remove(cours))
        if cours in self.parent().remoteInfo:
            coursWidget.setCheckState(QtCore.Qt.Checked)
        if not os.path.exists(self.parent().localdir + cours['path']):
            coursWidget.setDisabled(True)
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(coursWidget)
        
class AnimationWidget(QtGui.QWidget):
    def __init__(self, animation, parent=None):
        super(AnimationWidget, self).__init__(parent)
        transferInfo=self.parent().transferInfo
        transferInfo.append(animation)
        self.destroyed.connect(lambda _:transferInfo.remove(animation))
        nomWidget = QtGui.QLineEdit(animation['nom'])
        nomWidget.home(True)
        nomWidget.deselect()
        nomWidget.textChanged.connect(lambda text, animation=animation: animation.update({'nom': text}))            
        lienWidget = QtGui.QLineEdit(animation['lien'])
        lienWidget.home(True)
        lienWidget.deselect()
        lienWidget.textChanged.connect(lambda text, animation=animation: animation.update({'lien': text}))
        iconWidget = QtGui.QComboBox()
        icons = ["GeoGebra", "Flash", "JavaScript", "Python"]
        iconWidget.addItems(icons)
        iconWidget.setCurrentIndex(iconWidget.findText(animation['icon']))
        iconWidget.currentIndexChanged.connect(lambda index: animation.update({'icon': iconWidget.currentText()}))
        self.check = QtGui.QCheckBox()
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(lienWidget)
        layout.addWidget(iconWidget)
        layout.addWidget(self.check)
        
class ADSWidget(QtGui.QWidget):
    def __init__(self, ads, parent=None):
        super(ADSWidget, self).__init__(parent)
        transferInfo=self.parent().transferInfo
        transferInfo.append(ads)
        self.destroyed.connect(lambda _:transferInfo.remove(ads))
        nomWidget = QtGui.QLineEdit(ads['nom'])
        nomWidget.home(True)
        nomWidget.deselect()
        nomWidget.textChanged.connect(lambda text, ads=ads: ads.update({'nom': text}))            
        eleveWidget = QtGui.QLineEdit(ads['eleve'])
        eleveWidget.home(True)
        eleveWidget.deselect()
        eleveWidget.textChanged.connect(lambda text, ads=ads: ads.update({'eleve': text}))
        dateWidget = QtGui.QDateTimeEdit(QtCore.QDate.fromString(ads['date'], format=QtCore.Qt.DefaultLocaleLongDate))
        dateWidget.setCalendarPopup(True)
        dateWidget.dateChanged.connect(lambda date, ads=ads: ads.update({'date':date.toString(QtCore.Qt.DefaultLocaleLongDate)}))
        fileWidget = QtGui.QComboBox()
        fileWidget.addItems(os.listdir('ADS'))
        fileWidget.setCurrentIndex(fileWidget.findText(ads['fichier']))
        fileWidget.currentIndexChanged.connect(lambda text, ads=ads: ads.update({'fichier':text}))
        self.check = QtGui.QCheckBox()
        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(nomWidget)
        layout.addWidget(eleveWidget)
        layout.addWidget(dateWidget)
        layout.addWidget(fileWidget)
        layout.addWidget(self.check)
        
        
class WebSite(form_class, base_class):
    def __init__(self, parent=None):
        super(WebSite, self).__init__(parent)
        self.setupUi(self)
        self.addADSButton.setIcon(QtGui.QIcon(scriptdir + "/images/plus_32.ico"))
        self.removeADSButton.setIcon(QtGui.QIcon(scriptdir + "/images/delete_32.ico"))
        self.addAnimationsButton.setIcon(QtGui.QIcon(scriptdir + "/images/plus_32.ico"))
        self.removeAnimationsButton.setIcon(QtGui.QIcon(scriptdir + "/images/delete_32.ico"))
        self.transferButton.setIcon(QtGui.QIcon(scriptdir + "/images/ftp_64.png"))
        self.localdir = "E:/Documents/Enseignement/Corot/"
        self.remotedir = "E:/Documents/Enseignement/Test/"
        os.chdir(self.localdir)
        self.transferInfo = []
        self.getLocalInfo()
        self.getRemoteInfo()
        self.fillForms()

    def ones(self, t):
        return [e for e in self.localInfo if e['type'] == t]

    def pairs(self, typeEnonce, typeCorrige):
        enonces = sorted([e for e in self.localInfo if e['type'] == typeEnonce], key=lambda e:e['nom'])
        corriges = sorted([e for e in self.localInfo if e['type'] == typeCorrige], key=lambda e:e['nom'])
        return zip(enonces, corriges)
        
    def getRemoteInfo(self):
        try:
            with open(self.remotedir + "/app/data.json", "r", encoding='utf8') as f:
                self.remoteInfo = json.load(f)
        except:
            self.remoteInfo = []
            
    def getLocalInfo(self):
        self.localInfo = []
        for name in sorted(os.listdir('DS')):
            if 'DS' in name and os.path.isdir('DS/' + name):
                self.localInfo.append({'nom':name, 'type':'enonceDS', 'path':'DS/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':name, 'type':'corrigeDS', 'path':'DS/' + name + '/' + name + '_corrige.pdf'})
                
        for name in sorted(os.listdir('DM')):
            if 'DM' in name and os.path.isdir('DM/' + name):
                self.localInfo.append({'nom':name, 'type':'enonceDM', 'path':'DM/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':name, 'type':'corrigeDM', 'path':'DM/' + name + '/' + name + '_corrige.pdf'})
                
        for name in sorted(os.listdir('Cours')):
            if  os.path.isdir('Cours/' + name):
                s = read(self.localdir + "Cours/" + name + "/" + name + ".tex");
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'cours', 'path':'Cours/' + name + '/' + name + '.pdf'})
                
        for name in sorted(os.listdir('Formulaires')):
            if  os.path.isdir('Formulaires/' + name):
                s = read(self.localdir + "Formulaires/" + name + "/" + name + ".tex");
                titre = re.search(r"\\titreformulaire{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'formulaire', 'path':'Formulaires/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('Colles')):
            if 'ProgColles' in name and os.path.isdir('Colles/' + name):
                self.localInfo.append({'nom':name, 'type':'colle', 'path':'Colles/' + name + '/' + name + '.pdf'})

        for name in sorted(os.listdir('Interros')):
            if 'Interro' in name and os.path.isdir('Interros/' + name):
                self.localInfo.append({'nom':name, 'type':'interro', 'path':'Interros/' + name + '/' + name + '.pdf'})
                
        for name in sorted(os.listdir('TD')):
            if  os.path.isdir('TD/' + name):
                s = read(self.localdir + "TD/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'enonceTD', 'path':'TD/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':titre, 'type':'corrigeTD', 'path':'TD/' + name + '/' + name + '_corrige.pdf'})
                
        return
    
        for name in sorted(os.listdir('Info')):
            if  os.path.isdir('Info/' + name):
                s = read(self.localdir + "Info/" + name + "/" + name + ".tex");
                titre = re.search(r"\\titrecours{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'info', 'path':'Info/' + name + '/' + name + '.pdf'})
                
        for name in sorted(os.listdir('SlidesInfo')):
            if  os.path.isdir('SlidesInfo/' + name):
                s = read(self.localdir + "SlidesInfo/" + name + "/" + name + ".tex");
                titre = re.search(r"\\title{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'slidesinfo', 'path':'SlidesInfo/' + name + '/' + name + '.pdf'})
                
        for name in sorted(os.listdir('TDInfo')):
            if  os.path.isdir('TDInfo/' + name):
                s = read(self.localdir + "TDInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'enonceTDInfo', 'path':'TDInfo/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':titre, 'type':'corrigeTDInfo', 'path':'TDInfo/' + name + '/' + name + '_corrige.pdf'})
                
        for name in sorted(os.listdir('TPInfo')):
            if  os.path.isdir('TPInfo/' + name):
                s = read(self.localdir + "TPInfo/" + name + "/" + name + ".tex")
                titre = re.search(r"\\titretd{(.*?)}", s, re.DOTALL).group(1).replace('\\\\', ' ')
                self.localInfo.append({'nom':titre, 'type':'enonceTPInfo', 'path':'TPInfo/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':titre, 'type':'corrigeTPInfo', 'path':'TPInfo/' + name + '/' + name + '_corrige.pdf'})
            
        for name in sorted(os.listdir('DSInfo')):
            if 'DSInfo' in name and os.path.isdir('DSInfo/' + name):
                self.localInfo.append({'nom':name, 'type':'enonceDSinfo', 'path':'DSInfo/' + name + '/' + name + '.pdf'})
                self.localInfo.append({'nom':name, 'type':'corrigeDSinfo', 'path':'DSInfo/' + name + '/' + name + '_corrige.pdf'})
                

    def clearForms(self):            
        for form in (self.formDS, self.formDM, self.formColles, self.formCours, self.formInterros, self.formTD, self.formInfo, self.formTDInfo, self.formTPInfo, self.formADS, self.formFormulaires):
            if form is not None:
                while form.count():
                    item = form.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    
    def fillForms(self):
        for enonce, corrige in self.pairs('enonceDS', 'corrigeDS'):
            self.formDS.addWidget(EnonceCorrigeWidget(enonce, corrige, self))

        for enonce, corrige in self.pairs('enonceDM', 'corrigeDM'):
            self.formDM.addWidget(EnonceCorrigeWidget(enonce, corrige, self))
        
        for i, cours in enumerate(self.ones('cours')):
            self.formCours.addWidget(CoursWidget(cours, self), i / 4, i % 4)

        for i, formulaire in enumerate(self.ones('formulaire')):
            self.formFormulaires.addWidget(CoursWidget(formulaire, self), i / 4, i % 4)

        for i, colle in enumerate(self.ones('colle')):
            self.formColles.addWidget(CoursWidget(colle, self), i / 4, i % 4)
        
        for i, interro in enumerate(self.ones('interro')):
            self.formInterros.addWidget(CoursWidget(interro, self), i / 4, i % 4)

        for enonce, corrige in self.pairs('enonceTD', 'corrigeTD'):
            self.formTD.addWidget(EnonceCorrigeWidget(enonce, corrige, self))

        for i, info in enumerate(self.ones('info')):
            self.formInfo.addWidget(CoursWidget(info, self), i / 4, i % 4)

        for i, slidesinfo in enumerate(self.ones('slidesinfo')):
            self.formSlidesInfo.addWidget(CoursWidget(slidesinfo), i / 4, i % 4)

        for enonce, corrige in self.pairs('enonceTDInfo', 'corrigeTDInfo'):
            self.formTDInfo.addWidget(EnonceCorrigeWidget(enonce, corrige, self))

        for enonce, corrige in self.pairs('enonceTPInfo', 'corrigeTPInfo'):
            self.formTPInfo.addWidget(EnonceCorrigeWidget(enonce, corrige, self))

        for enonce, corrige in self.pairs('enonceDSinfo', 'corrigeDSinfo'):
            self.formDSInfo.addWidget(EnonceCorrigeWidget(enonce, corrige, self))
            
        for animation in [e for e in self.remoteInfo if e['type'] == 'animation']:
            self.formAnimations.addWidget(AnimationWidget(animation, self))
            
        return

        self.populateADS()
        self.populateAnimations()
        
    def writeTransferInfo(self):
        with open(self.remotedir + "/app/data.json", "w", encoding='utf8') as f:
            json.dump(self.transferInfo, f);
            f.close()
            
    def transferFiles(self):
        filesToCopy=[e['path'] for e in self.transferInfo if 'path' in e.keys()]
        filesToDelete=[e['path'] for e in self.remoteInfo if 'path' in e.keys() and e not in self.transferInfo]
        
        # # heroku
              
    @QtCore.pyqtSlot()
    def on_addADSButton_clicked(self):
        ads = {'nom':'', 'eleve':'', 'type':'ads', 'date':'', 'fichier':''}
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
        animation = {'nom':'', 'lien':'', 'type':'animation', 'icon':''}
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
        self.message = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Sauvegarde", "Sauvegarde", QtGui.QMessageBox.Cancel)
        self.message.setInformativeText("Sauvegarde en cours")
        self.message.show()
        self.writeTransferInfo()
        self.message.setInformativeText("Sauvegarde terminée")
                
if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    app = QtGui.QApplication(sys.argv)
    myWebSite = WebSite()
    myWebSite.show()
    sys.exit(app.exec_())
