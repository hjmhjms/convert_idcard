from io import BytesIO
import PIL.Image as Image
import app
import time
import excel_reader
from selenium.common.exceptions import NoSuchElementException
import os
import copy


#
#
# 丛龙海外旗舰店:技术
# qwer147852

# https://certify.tmall.hk/idcard/info.htm?spm=a1z09.1.0.0.6ef53606KVmF4u&id=1694059164476038168

def Init_OnSubProcess(s_bRunning, WebDriverObj, nMark, LockObj,dictConfig):
    WebDriverObj.SetUrl(
        "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?mytmenu=ymbb&spm=a217wi.openworkbeanchtmall_web")
    WebDriverObj.GetEngineDriverObj().find_element_by_link_text('密码登录').click()
    WebDriverObj.GetEngineDriverObj().find_element_by_name('fm-login-password').send_keys(dictConfig["密码"])
    WebDriverObj.GetEngineDriverObj().find_element_by_name('fm-login-id').send_keys(dictConfig["用户名"])
    WebDriverObj.GetEngineDriverObj().find_element_by_class_name("fm-submit").click()
    WebDriverObj.WaitTitle(s_bRunning, "天猫千牛工作台")


def DoJob_OnSubProcess(s_bRunning, WebDriverObj, wsRequest, nMark, LockObj):
    orderid, dictOrder, szOutDir = wsRequest

    WebDriverObj.SetUrlUntilSucc(s_bRunning, f"https://certify.tmall.hk/idcard/info.htm?id={orderid}")
    bHaveIdCard = False
    try:
        WebDriverObj.GetEngineDriverObj().find_element_by_class_name("sfz-info")
        bHaveIdCard = True
    except NoSuchElementException as e:
        bHaveIdCard = False

    if not bHaveIdCard:
        return dictOrder

    # 获取基本信息
    dictOrder["身份证"] = WebDriverObj.GetEngineDriverObj().find_element_by_xpath(
        '//*[@id="id-card"]/div[2]/table/tbody/tr[3]/td[2]').text
    dictOrder["姓名"] = WebDriverObj.GetEngineDriverObj().find_element_by_xpath(
        '//*[@id="id-card"]/div[2]/table/tbody/tr[2]/td[2]').text

    # 获取图片
    WebDriverObj.SetUrlUntilSucc(s_bRunning, f'https://certify.tmall.hk/idcard/image.htm?id={orderid}&t=1')
    screenshot1 = WebDriverObj.GetEngineDriverObj().get_screenshot_as_png()
    WebDriverObj.SetUrlUntilSucc(s_bRunning, f'https://certify.tmall.hk/idcard/image.htm?id={orderid}&t=2')
    screenshot2 = WebDriverObj.GetEngineDriverObj().get_screenshot_as_png()

    from_image1 = Image.open(BytesIO(screenshot1))
    from_image2 = Image.open(BytesIO(screenshot2))
    w = max(from_image1.size[0], from_image2.size[0])
    h = max(from_image1.size[1], from_image2.size[1])
    to_image = Image.new('RGB', (w, h * 2))
    to_image.paste(from_image1, (0, 0))
    to_image.paste(from_image2, (0, h))
    to_image.save(os.path.join(szOutDir, f'{dictOrder["身份证"]}.jpg'))
    return dictOrder


class CongLongApp(app.App):
    def __init__(self):
        super().__init__(Init_OnSubProcess, DoJob_OnSubProcess)

    def Init(self):
        super().Init()

        self.CalcJob()
        self.ReCreateOutFile()

    def GetOutFilePath(self):
        orderPath = self.GetConfig()["输出订单"]
        if not os.path.isabs(orderPath):
            #curDir = os.path.dirname(os.path.abspath(__file__))
            curDir = os.getcwd()
            orderPath = os.path.join(curDir, orderPath)

        return orderPath

    def ReCreateOutFile(self):
        szPath = self.GetOutFilePath()
        if os.path.exists(szPath):
            os.remove(szPath)
        self.WriteOutFile([["交易订单号", "身份证", "姓名"]])

    def WriteOutFile(self, listValue):
        szPath = self.GetOutFilePath()
        excel_reader.WriteExcelAppend(szPath, listValue)

    def CalcJob(self):
        dictOrders = self.GetJobList()
        print(f"一共要处理{len(dictOrders)}个job")

        # 身份证输出目录
        szOutDir = self.GetIdcardOutDir()
        os.makedirs(szOutDir, exist_ok=True)

        for orderid, dictOneOrder in dictOrders.items():
            self.AddJob((orderid, copy.deepcopy(dictOneOrder), szOutDir))  # 交易订单号

    def GetIdcardOutDir(self):
        szPath = self.GetConfig()["身份证输出目录"]
        if not os.path.isabs(szPath):
            #curDir = os.path.dirname(os.path.abspath(__file__))
            curDir = os.getcwd()
            szPath = os.path.join(curDir, szPath)
        return szPath

    def GetJobList(self):
        orderPath = self.GetConfig()["输入订单"]
        if not os.path.isabs(orderPath):
            #curDir = os.path.dirname(os.path.abspath(__file__))
            curDir = os.getcwd()
            orderPath = os.path.join(curDir, orderPath)

        print(f"读取订单xls:{orderPath}")
        dictOrders, listKeyIndex = excel_reader.ReadExcelFileData(orderPath)
        dictRet = {}
        for orderid, dictOneOrder in dictOrders.items():
            if len(dictOneOrder.get("身份证", "")) == 0:
                dictRet[orderid] = dictOneOrder
        return dictRet

    def DispatchResult(self, result):
        orderid = result.get("交易订单号", "")
        idcard = result.get("身份证", "")
        name = result.get("姓名", "")
        if orderid:
            listValue = [[orderid, idcard, name]]
            self.WriteOutFile(listValue)
        print(f'完成 {result}')
