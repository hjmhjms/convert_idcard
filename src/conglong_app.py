from io import BytesIO
import PIL.Image as Image
import app
import time
import excel_reader
from selenium.common.exceptions import NoSuchElementException
import os


#
#
# 丛龙海外旗舰店:技术
# qwer147852

# https://certify.tmall.hk/idcard/info.htm?spm=a1z09.1.0.0.6ef53606KVmF4u&id=1694059164476038168

class CongLongApp(app.App):
    def __init__(self):
        super().__init__()

    def Loop(self):
        self.GetWebDriver().SetUrl(
            "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?mytmenu=ymbb&spm=a217wi.openworkbeanchtmall_web")
        self.GetWebDriver().GetEngineDriverObj().find_element_by_link_text('密码登录').click()
        self.GetWebDriver().GetEngineDriverObj().find_element_by_name('fm-login-password').send_keys(r'qwer147852')
        self.GetWebDriver().GetEngineDriverObj().find_element_by_name('fm-login-id').send_keys(r'丛龙海外旗舰店:技术')
        self.GetWebDriver().GetEngineDriverObj().find_element_by_class_name("fm-submit").click()
        self.GetWebDriver().WaitTitle("天猫千牛工作台")

        dictOrderList, listKeyIndex = self.GetJobList()
        # 身份证输出目录
        szOutDir = self.GetIdcardOutDir()
        os.makedirs(szOutDir, exist_ok=True)

        # print(dictOrderList, listKeyIndex)

        nB = time.time()
        i = 0
        nSucc = 0
        nFail = 0
        for orderid, dictOrder in dictOrderList.items():
            # i += 1
            # if i > 3:
            #     break
            if self.DoOneOrder(orderid, dictOrder, szOutDir):
                nSucc += 1
            else:
                nFail += 1

        nC = time.time()

        print("耗时", nSucc, nFail, nC - nB)
        while self.IsRunning():
            time.sleep(1)

    def GetIdcardOutDir(self):
        szPath = self.GetConfig()["身份证输出目录"]
        if not os.path.isabs(szPath):
            curDir = os.path.dirname(os.path.abspath(__file__))
            szPath = os.path.join(curDir, szPath)
        return szPath

    def GetJobList(self):
        orderPath = self.GetConfig()["输入订单"]
        if not os.path.isabs(orderPath):
            curDir = os.path.dirname(os.path.abspath(__file__))
            orderPath = os.path.join(curDir, orderPath)

        print(f"读取订单xls:{orderPath}")
        dictOrderList, listKeyIndex = excel_reader.ReadExcelFileData(orderPath)
        return dictOrderList, listKeyIndex

    def DoOneOrder(self, orderid, dictOrder, szOutImgDir):
        self.GetWebDriver().SetUrlUntilSucc(f"https://certify.tmall.hk/idcard/info.htm?id={orderid}")
        bHaveIdCard = False
        try:
            self.GetWebDriver().GetEngineDriverObj().find_element_by_class_name("sfz-info")
            bHaveIdCard = True
        except NoSuchElementException as e:
            bHaveIdCard = False

        if not bHaveIdCard:
            print(f"{orderid}:无身份证")
            return False

        # 获取基本信息
        dictOrder["身份证"] = repr(self.GetWebDriver().GetEngineDriverObj().find_element_by_xpath(
            '//*[@id="id-card"]/div[2]/table/tbody/tr[3]/td[2]').text)
        dictOrder["姓名"] = repr(self.GetWebDriver().GetEngineDriverObj().find_element_by_xpath(
            '//*[@id="id-card"]/div[2]/table/tbody/tr[2]/td[2]').text)
        print(f'{orderid}:有身份证,{dictOrder["身份证"]},{dictOrder["姓名"]}')

        # 获取图片
        self.GetWebDriver().SetUrlUntilSucc(f'https://certify.tmall.hk/idcard/image.htm?id={orderid}&t=1')
        screenshot1 = self.GetWebDriver().GetEngineDriverObj().get_screenshot_as_png()
        self.GetWebDriver().SetUrlUntilSucc(f'https://certify.tmall.hk/idcard/image.htm?id={orderid}&t=2')
        screenshot2 = self.GetWebDriver().GetEngineDriverObj().get_screenshot_as_png()

        from_image1 = Image.open(BytesIO(screenshot1))
        from_image2 = Image.open(BytesIO(screenshot2))
        w = max(from_image1.size[0], from_image2.size[0])
        h = max(from_image1.size[1], from_image2.size[1])
        to_image = Image.new('RGB', (w, h * 2))
        to_image.paste(from_image1, (0, 0))
        to_image.paste(from_image2, (0, h))
        to_image.save(os.path.join(szOutImgDir, f'{dictOrder["身份证"]}.jpg'))
        print(f'order: {orderid} finfish')
        return True
