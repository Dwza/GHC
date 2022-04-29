import yaml
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox
from UI.ghc import Ui_QFrmMain
import math
from os.path import exists
from UI.config import Ui_QFrmConfig


class FrmMain(QMainWindow, Ui_QFrmMain):

    totalTokens = 0
    cfgFile = 'ghc.yml'
    cfg = {}
    saveOnStart = False

    def __init__(self):
        super(FrmMain, self).__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle('Great Hall Calculator - Level 0/240')
        self.loadConfigs()
        self.loadData()
        self.bindHandlers()
        self.configUi = Ui_QFrmConfig()
        self.setFocus()
        
    """
    def openConfigWindow(self):
        self.window = QMainWindow()
        self.ui = Ui_QFrmConfig()
        self.ui.setupUi(self.window)
        self.window.show()
    """

    @staticmethod
    def createYaml(file):
        stdConfig = {
            "settings": {
                "load_on_start": False,
            },
            "configs": {
                "cb_stage": 1,
                "tokens": 0,
                "maxNeededTokens": 102600,
                "sections": ['m', 's', 'f', 'v'],
                "stageTokens": [2, 2, 3, 4, 4],
                "subFromLvl": [12.5, 50, 125, 325, 575, 875, 1575, 2375, 3275, 4275],
                "totalTokens": 102600
            },
            "ranks": {
                "cb_m_1": 0,
                "cb_m_2": 0,
                "cb_m_3": 0,
                "cb_m_4": 0,
                "cb_m_5": 0,
                "cb_m_6": 0,
                "cb_s_1": 0,
                "cb_s_2": 0,
                "cb_s_3": 0,
                "cb_s_4": 0,
                "cb_s_5": 0,
                "cb_s_6": 0,
                "cb_f_1": 0,
                "cb_f_2": 0,
                "cb_f_3": 0,
                "cb_f_4": 0,
                "cb_f_5": 0,
                "cb_f_6": 0,
                "cb_v_1": 0,
                "cb_v_2": 0,
                "cb_v_3": 0,
                "cb_v_4": 0,
                "cb_v_5": 0,
                "cb_v_6": 0,
            }
        }
        with open(file, 'w') as ghd:
            yaml.dump(stdConfig, ghd)

    @staticmethod
    def setCBColor(cb, rank):
        color = "none"
        if rank > 0:
            color = "#d65d00"
        if rank > 3:
            color = "#0f80bd"
        if rank > 6:
            color = "#ffd103"

        cb.setStyleSheet("border: 2px solid " + color + ";font-weight: bold")

    @staticmethod
    def toInt(v):
        return v != '' and int(v) or 0

    def loadConfigs(self):
        if not exists(self.cfgFile):
            self.createYaml(self.cfgFile)
            print(self.cfgFile + " file has been created since there was no file before.")

        with open(self.cfgFile, "r") as cfg:
            self.cfg = yaml.load(cfg, Loader=yaml.FullLoader)

        self.totalTokens = self.cfg['configs']['totalTokens']

    def saveData(self):
        s = 0
        for affinity in self.cfg['configs']['sections']:
            for cbId in range(6):
                cbName = "cb_" + affinity + "_" + str(cbId+1)
                cb = self.findChild(QComboBox, cbName)
                v = self.toInt(cb.currentIndex())
                self.cfg['ranks'][cbName] = v
                s = s + v

        self.cfg['configs']['cb_stage'] = self.toInt(self.cb_stage.currentText())
        self.cfg['configs']['tokens'] = self.toInt(self.sb_tokens.text())
        self.setWindowTitle('Great Hall Calculator - Level ' + str(s) + '/240')

        with open(self.cfgFile, 'w') as cfg:
            yaml.dump(self.cfg, cfg)

    def loadData(self):
        s = 0
        sections = self.cfg['configs']['sections']
        for affinity in sections:
            for cbId in range(6):
                cbName = "cb_" + affinity + "_" + str(cbId+1)
                cb = self.findChild(QComboBox, cbName)
                v = self.cfg['ranks'][cbName]
                self.setCBColor(cb, v)
                cb.setCurrentIndex(v)
                if v != 0:
                    s = s + v

        self.cb_stage.setCurrentIndex(self.cfg['configs']['cb_stage']-1)
        self.sb_tokens.setValue(self.cfg['configs']['tokens'])
        self.calcTotalNeededTokens()
        self.refreshLabels()
        self.setWindowTitle('Great Hall Calculator - Level ' + str(s) + '/240')

    def refreshLabels(self):
        self.refreshTokenPerWin()
        self.refreshTokensToEnd()
        self.refreshNeededArenaWins()

    def stageChangeHandler(self):
        self.calcTotalNeededTokens()
        self.refreshLabels()
        self.saveData()

    def refreshTokenPerWin(self):
        stage = self.cb_stage.currentIndex()
        self.lcdTokens.display(self.cfg['configs']['stageTokens'][stage])

    def refreshTokensToEnd(self):
        self.lcdEnd.display(self.totalTokens)

    def refreshNeededArenaWins(self):
        wins = self.totalTokens/self.getTokenPerWin()
        self.lcdWins.display(int(math.ceil(wins)))

    def getTokenPerWin(self):
        stage = self.cb_stage.currentText()
        return self.cfg['configs']['stageTokens'][int(stage) - 1]

    def bindHandlers(self):
        for affinity in self.cfg['configs']['sections']:
            for cbId in range(6):
                cb = self.findChild(QComboBox, "cb_" + affinity + "_" + str(cbId+1))
                cb.currentIndexChanged.connect(self.stageChangeHandler)
        self.cb_stage.currentIndexChanged.connect(self.stageChangeHandler)
        self.sb_tokens.textChanged.connect(self.stageChangeHandler)

    def subtractExistingTokens(self):
        existingTokens = self.sb_tokens.text()
        if existingTokens != '':
            self.totalTokens = self.totalTokens - int(existingTokens)

    def calcTotalNeededTokens(self):
        self.totalTokens = self.cfg['configs']['maxNeededTokens']
        for affinity in self.cfg['configs']['sections']:
            for cbId in range(6):
                cb = self.findChild(QComboBox, "cb_" + affinity + "_" + str(cbId+1))
                v = self.toInt(cb.currentIndex())
                self.setCBColor(cb, v)
                if v > 0:
                    self.totalTokens = self.totalTokens - self.cfg['configs']['subFromLvl'][v-1]
        self.subtractExistingTokens()


app = QApplication()
frm_Main = FrmMain()
frm_Main.show()
app.exec()
