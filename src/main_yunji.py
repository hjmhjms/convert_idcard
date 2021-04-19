import signal
import time
import sys
import jm_webdriver
import os
import json
import excel_reader
import multiprocessing
import http_proxy

def Main():
    import yunji_app
    myapp = yunji_app.YunJiApp()
    myapp.Init()
    myapp.Loop()
    myapp.Unit()
    print("exit")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    http_proxy.freeze_support()
    Main()
    sys.exit(0)
    print("finish")


