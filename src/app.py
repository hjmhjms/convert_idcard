import builtins
import signal
import time
import jm_webdriver
import os
import json
import multiprocessing
import queue
import sys


def Main_OnSubProcess(s_bRunning, queueJob, queueResult, nMark, lock, Init_OnSubProcess, DoJob_OnSubProcess):
    WebDriverObj = jm_webdriver.JmWebDriver(bShow=True)

    def OnSignalCallback(s, f):
        print(f"Main_OnSubProcess:{nMark} OnSignalCallback")
        s_bRunning.value = False
        WebDriverObj.Destroy()
        sys.exit(0)

    signal.signal(signal.SIGINT, OnSignalCallback)
    signal.signal(signal.SIGILL, OnSignalCallback)

    Init_OnSubProcess(s_bRunning, WebDriverObj, nMark, lock)

    try:
        while s_bRunning.value:
            while s_bRunning.value:
                try:
                    wsRequest = queueJob.get(False)
                    result = DoJob_OnSubProcess(s_bRunning, WebDriverObj, wsRequest, nMark, lock)
                    queueResult.put(result)
                except queue.Empty:
                    break
            time.sleep(0.03)
    except Exception as e:
        print(e)
    WebDriverObj.Destroy()

    print(f"Main_OnSubProcess{nMark} exit")


def Init_OnSubProcess(s_bRunning, WebDriverObj, nMark, LockObj):
    pass


def DoJob_OnSubProcess(s_bRunning, WebDriverObj, wsRequest, nMark, LockObj):
    return None


class App:
    def __init__(self, Init_OnSubProcess, DoJob_OnSubProcess):
        builtins.theApp = self
        self.m_ProxyProcessObj = jm_webdriver.JmProxyProcess()
        self.m_listWebDriverObj = []
        self.ms_bRunning = multiprocessing.Value('b', False)
        self.m_dictConfig = {}
        self.m_queueJob = multiprocessing.Queue(100000)
        self.m_queueResult = multiprocessing.Queue(100000)
        self.m_lock = multiprocessing.Lock()
        self.m_nProcesses = 1
        self.m_listProcessesObj = []
        self.m_Init_OnSubProcess = Init_OnSubProcess
        self.m_DoJob_OnSubProcess = DoJob_OnSubProcess

    # -----------------------------------

    def InitProcesses(self):
        self.m_nProcesses = self.m_dictConfig.get("并发多少个", 1)
        for i in range(self.m_nProcesses):
            process = multiprocessing.Process(target=Main_OnSubProcess,
                                              args=(
                                              self.ms_bRunning, self.m_queueJob, self.m_queueResult, i, self.m_lock,
                                              self.m_Init_OnSubProcess, self.m_DoJob_OnSubProcess))
            process.start()
            self.m_listProcessesObj.append(process)
            time.sleep(2)

    # -----------------------------------

    def JoinProcesses(self):
        for p in self.m_listProcessesObj:
            p.join()
        print("JoinProcesses")

    def InitWebProxy(self):
        self.m_ProxyProcessObj.Start()

    def InitConfig(self):
        curDir = os.path.dirname(os.path.abspath(__file__))
        configFile = os.path.join(curDir, "config.json")
        try:
            with open(configFile, "r", encoding="utf-8") as FileObj:
                self.m_dictConfig = json.load(FileObj)
        except Exception as ErrObj:
            print("load config", str(ErrObj))

    def Init(self):
        if self.ms_bRunning.value:
            return

        self.ms_bRunning.value = True
        self.InitConfig()
        self.InitSignal()
        self.InitWebProxy()
        time.sleep(1)
        self.InitProcesses()

    def InitSignal(self):
        signal.signal(signal.SIGINT, self.OnSignalCallback)
        signal.signal(signal.SIGILL, self.OnSignalCallback)

    def OnSignalCallback(self, s, f):
        print("ctrl+c11111111")
        self.ms_bRunning.value = False

    def Unit(self):
        self.JoinProcesses()
        self.m_ProxyProcessObj.Stop()

    def IsRunning(self):
        return self.ms_bRunning.value

    def Loop(self):
        pass

    def GetConfig(self):
        return self.m_dictConfig

    def AddJob(self, job):
        self.m_queueJob.put(job)

    def AddResult(self, result):
        self.m_queueResult.put(result)

    def Loop(self):
        while self.ms_bRunning.value:
            while self.ms_bRunning.value:
                try:
                    result = self.m_queueResult.get(False)
                    self.DispatchResult(result)
                except queue.Empty:
                    break
            time.sleep(0.3)

    def DispatchResult(self, result):
        pass
