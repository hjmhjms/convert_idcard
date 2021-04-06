import signal
import time
import sys
import jm_webdriver
import os
import json
import excel_reader


def Main():
    import conglong_app
    myapp = conglong_app.CongLongApp()
    myapp.Init()
    myapp.Loop()
    myapp.Unit()
    print("exit")


if __name__ == '__main__':
    Main()
