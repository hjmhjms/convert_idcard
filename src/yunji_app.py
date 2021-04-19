from io import BytesIO
import PIL.Image as Image
import app
import time
import excel_reader
from selenium.common.exceptions import NoSuchElementException
import os
import copy
import requests
import urllib3

urllib3.disable_warnings()


# https://certify.tmall.hk/idcard/info.htm?spm=a1z09.1.0.0.6ef53606KVmF4u&id=1694059164476038168

def SetWebMessage(WebDriverObj, szMsg):
    html_content = f"""
    <html>
         <head></head>
         <body>
             <div>
                 {szMsg}
             </div>
         </body>
    </html>
    """
    WebDriverObj.GetEngineDriverObj().get("data:text/html;charset=utf-8," + html_content)


def Init_OnSubProcess(s_bRunning, WebDriverObj, nMark, LockObj, dictConfig):
    WebDriverObj.SetUrl("https://seller.yunjiglobal.com/popadminweb/login")
    WebDriverObj.WaitTitle(s_bRunning, "云集 - 商家后台")
    WebDriverObj.GetEngineDriverObj().find_element_by_name('accounts').send_keys(dictConfig["用户名"])
    WebDriverObj.GetEngineDriverObj().find_element_by_name('password').send_keys(dictConfig["密码"])
    WebDriverObj.GetEngineDriverObj().find_element_by_class_name("loginBtn").click()
    WebDriverObj.WaitUrlContain(s_bRunning, "index")


def DoJob_OnSubProcess(s_bRunning, WebDriverObj, wsRequest, nMark, LockObj):
    orderid, dictOrder, szOutDir = wsRequest

    # 获取图片
    # WebDriverObj.SetUrlUntilSucc(s_bRunning,
    #                             f'https://seller.yunjiglobal.com/popadmin/admin/order/delivery/downIdentityCard?srcOrderId={orderid}&type=1&h=1')
    # screenshot1 = WebDriverObj.GetEngineDriverObj().get_screenshot_as_png()

    # cookie-----------------
    sel_cookies = WebDriverObj.GetEngineDriverObj().get_cookies()
    jar = requests.cookies.RequestsCookieJar()

    for i in sel_cookies:
        # 将selenium侧获取的完整cookies的每一个cookie名称和值传入RequestsCookieJar对象
        # domain和path为可选参数，主要是当出现同名不同作用域的cookie时，为了防止后面同名的cookie将前者覆盖而添加的
        jar.set(i['name'], i['value'], domain=i['domain'], path=i['path'])

    session = requests.session()  # requests以session会话形式访问网站
    session.cookies.update(jar)  # 将配置好的RequestsCookieJar对象加入到requests形式的session会话中

    # -----------------
    szUrl1 = f'https://seller.yunjiglobal.com/popadmin/admin/order/delivery/downIdentityCard?srcOrderId={orderid}&type=1&h=1'
    szUrl2 = f'https://seller.yunjiglobal.com/popadmin/admin/order/delivery/downIdentityCard?srcOrderId={orderid}&type=2&h=1'

    requestObj1 = requests.Request(method='GET', url=szUrl1)
    # verify设置为False来规避SSL证书验证
    responseObj1 = session.send(session.prepare_request(requestObj1), verify=False, timeout=20)
    requestObj2 = requests.Request(method='GET', url=szUrl2)
    responseObj2 = session.send(session.prepare_request(requestObj2), verify=False, timeout=20)

    # print(111111111111111111111111111111,responseObj,responseObj.status_code)

    # -----------------------------------------------------------
    # #r=requests.get(f'https://seller.yunjiglobal.com/popadmin/admin/order/delivery/downIdentityCard?srcOrderId={orderid}&type=1&h=1')
    #
    #
    # with open('e:/baidu.jpg', 'wb') as f:
    #     # 对于图片类型的通过r.content方式访问响应内容，将响应内容写入baidu.png中
    #     f.write(responseObj.content)

    #    time.sleep(500)

    ##    WebDriverObj.SetUrlUntilSucc(s_bRunning,
    #                                f'https://seller.yunjiglobal.com/popadmin/admin/order/delivery/downIdentityCard?srcOrderId={orderid}&type=2&h=1')
    #   screenshot2 = WebDriverObj.GetEngineDriverObj().get_screenshot_as_png()

    from_image1 = Image.open(BytesIO(responseObj1.content))
    from_image2 = Image.open(BytesIO(responseObj2.content))
    w = max(from_image1.size[0], from_image2.size[0])
    h = max(from_image1.size[1], from_image2.size[1])
    to_image = Image.new('RGB', (w, h * 2))
    to_image.paste(from_image1, (0, 0))
    to_image.paste(from_image2, (0, h))
    to_image.save(os.path.join(szOutDir, f'{dictOrder["收货人身份证号"]}.jpg'))

    return dictOrder


class YunJiApp(app.App):
    def __init__(self):
        super().__init__(Init_OnSubProcess, DoJob_OnSubProcess)

    def Init(self):
        super().Init()

        self.CalcJob()
        self.ReCreateOutFile()

    def GetOutFilePath_HaveID(self):
        orderPath = self.GetConfig()["输出有身份证订单"]
        if not os.path.isabs(orderPath):
            curDir = os.getcwd()
            orderPath = os.path.join(curDir, orderPath)
        return orderPath

    def GetOutFilePath_NoID(self):
        orderPath = self.GetConfig()["输出无身份证订单"]
        if not os.path.isabs(orderPath):
            curDir = os.getcwd()
            orderPath = os.path.join(curDir, orderPath)
        return orderPath

    def ReCreateOutFile(self):
        szPath = self.GetOutFilePath_HaveID()
        if os.path.exists(szPath):
            os.remove(szPath)

        szPath = self.GetOutFilePath_NoID()
        if os.path.exists(szPath):
            os.remove(szPath)

        self.WriteOutFile_HaveID([["交易订单号", "身份证", "姓名"]])
        self.WriteOutFile_NoID([["交易订单号", "身份证", "姓名"]])

    def WriteOutFile_HaveID(self, listValue):
        szPath = self.GetOutFilePath_HaveID()
        excel_reader.WriteExcelAppend(szPath, listValue)

    def WriteOutFile_NoID(self, listValue):
        szPath = self.GetOutFilePath_NoID()
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
            # curDir = os.path.dirname(os.path.abspath(__file__))
            curDir = os.getcwd()
            szPath = os.path.join(curDir, szPath)
        return szPath

    def GetJobList(self):
        orderPath = self.GetConfig()["输入订单"]
        if not os.path.isabs(orderPath):
            # curDir = os.path.dirname(os.path.abspath(__file__))
            curDir = os.getcwd()
            orderPath = os.path.join(curDir, orderPath)

        print(f"读取订单xls:{orderPath}")
        dictOrders, listKeyIndex = excel_reader.ReadExcelFileData(orderPath)
        return dictOrders

    def DispatchResult(self, result):
        orderid = result.get("交易订单号", "")
        idcard = result.get("身份证", "")
        name = result.get("姓名", "")
        #if orderid:
        #    listValue = [[orderid, idcard, name]]
        #    if idcard:
        #        self.WriteOutFile_HaveID(listValue)
        #    else:
        #        self.WriteOutFile_NoID(listValue)
        print(f'完成 {result}')


##    SetWebMessage(WebDriverObj, f'完成：订单编号:{dictOrder["订单编号"]},"收货人身份证号":{dictOrder.get("收货人身份证号","")},"收件人":{dictOrder.get("收件人","")}')