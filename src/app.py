import builtins
import signal
import time
import jm_webdriver
import os
import json


class App:
    def __init__(self):
        builtins.theApp = self
        self.m_ProxyProcessObj = jm_webdriver.JmProxyProcess()
        self.m_WebDriverObj = jm_webdriver.JmWebDriver(bShow=True)
        self.m_bRunning = False
        self.m_dictConfig = {}

    def InitConfig(self):
        curDir = os.path.dirname(os.path.abspath(__file__))
        configFile = os.path.join(curDir, "config.json")
        try:
            with open(configFile, "r", encoding="utf-8") as FileObj:
                self.m_dictConfig = json.load(FileObj)
        except Exception as ErrObj:
            print("load config", str(ErrObj))

    def Init(self):
        if self.m_bRunning:
            return

        self.m_bRunning = True
        self.InitConfig()
        self.InitSignal()
        self.m_ProxyProcessObj.Start()
        time.sleep(1)

    def InitSignal(self):
        signal.signal(signal.SIGINT, self.OnSignalCallback)

    def OnSignalCallback(self, s, f):
        print("ctrl+c")
        self.m_bRunning = False

    def Unit(self):
        self.m_WebDriverObj.Destroy()
        self.m_ProxyProcessObj.Stop()

    def IsRunning(self):
        return self.m_bRunning

    def GetWebDriver(self):
        return self.m_WebDriverObj

    def Loop(self):
        pass

    def GetConfig(self):
        return self.m_dictConfig
