from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import ActionChains
from PIL import Image
from datetime import date, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import platform
import os
import selenium
from multiprocessing import Process


class JmProxyProcess:
    def __init__(self):
        self.m_ProxyProcessObj = None

    def Start(self):
        if self.m_ProxyProcessObj is None:
            print("JmProxyProcess start")
            self.m_ProxyProcessObj = Process(target=self._ProxyProcessRun)
            self.m_ProxyProcessObj.start()


    def Stop(self):
        if self.m_ProxyProcessObj is not None:
            print("JmProxyProcess stop")
            self.m_ProxyProcessObj.join()
            self.m_ProxyProcessObj = None

    def _ProxyProcessRun(self):
        from mitmproxy.tools._main import mitmweb, mitmdump
        # mitmweb(args=['-s', './http_proxy.py', '-p', '18321', '--web-port', '18323'])
        mitmdump(args=['-s', './src/http_proxy.py', '-p', '18321', '-q'])


class JmWebDriver:
    def __init__(self, bShow=False):
        chromedriverPath1 = os.path.join(os.getcwd(),"tools", "chromedriver.exe")
        chromedriverPath2 = os.path.join(os.getcwd(),"..","tools", "chromedriver.exe")
        print(chromedriverPath1)
        print(chromedriverPath2)

        if os.path.isfile(chromedriverPath1):
            chromedriverPath = chromedriverPath1
        elif os.path.isfile(chromedriverPath2):
            chromedriverPath = chromedriverPath2
        else:
            chromedriverPath = None

        assert chromedriverPath, "驱动不存在"

        # -----------------------------------------
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

        if not bShow:
            options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # prefs = {"profile.managed_default_content_settings.images": 2, 'download.default_directory': os.path.dirname(os.path.realpath(__file__))+"/temp"} # 1是加载图片，2是不加载图片
        # options.add_experimental_option("prefs", prefs)
        options.add_argument('--proxy-server=http://127.0.0.1:18321')
        options.add_argument('disable-infobars')
        options.add_argument('--no-sandbox')
        # -----------------------------------------

        self.m_DriverObj = webdriver.Chrome(chrome_options=options,
                                            executable_path=chromedriverPath)
        # self.m_DriverObj.set_window_position(-10000, 0)
        self.m_DriverObj.set_window_position(0, 0)
        self.m_DriverObj.set_window_size(1600, 800)
        print("InitDriver succ")

    def SetUrlUntilSucc(self, s_bRunning, szUrl):
        print(f"SetUrlUntilSucc {szUrl}")
        while s_bRunning.value:
            try:
                self.m_DriverObj.set_page_load_timeout(30)
                self.m_DriverObj.get(szUrl)
                break
            except Exception as e:
                print(e)
                import traceback
                traceback.print_stack()

    def SetUrl(self, szUrl):
        self.m_DriverObj.set_page_load_timeout(30)
        self.m_DriverObj.get(szUrl)

    def Test(self):
        ff1 = '// *[ @ id = "__layout"] / div / div[4] / div / div[2] / div / div[1] / div / div / div[1]'
        v1 = repr(self.m_DriverObj.find_element_by_xpath(ff1).text)

        # listName = driver.find_elements_by_class_name("symbol-name")

    def WaitTitle(self, s_bRunning, szTitle):
        while s_bRunning.value:
            try:
                WebDriverWait(self.m_DriverObj, 0.5).until(ec.title_is(szTitle))  # 等待元素出现
                return
            except selenium.common.exceptions.TimeoutException as e:
                continue
            except Exception as e:
                continue

    def GetEngineDriverObj(self):
        return self.m_DriverObj

    def Destroy(self):
        if self.m_DriverObj:
            self.m_DriverObj.quit()
            self.m_DriverObj = None


'''
from selenium import webdriver
driver_path = r'D:\python\geckodriver-v0.23.0-win64\geckodriver.exe'
driver = webdriver.Firefox(executable_path=driver_path)
driver.get("https://www.52pojie.cn/")
driver.execute_script("window.open('https://www.xd0.com/')") # 打开多个窗口
print(driver.window_handles) # 打印当前所有窗口
driver.switch_to_window(driver.window_handles[0]) # 切换到第一个窗口
print(driver.current_url)
# print(driver.page_source)
'''
