from selenium import webdriver
import time
from PIL import Image
from selenium.webdriver import ActionChains

#初始
def main():
    bro = webdriver.Chrome(executable_path="G:/work/waibao/convert_idcard/tools/chromedriver-release.exe")
    bro.maximize_window()

    bro.get("https://login.taobao.com/member/login.jhtml")
    time.sleep(1)

    bro.find_element_by_name("fm-login-id").send_keys('丛龙海外旗舰店: 技术')
    time.sleep(1)
    bro.find_element_by_name("fm-login-password").send_keys('qwer147852')
    time.sleep(1)

    GetImage(bro)

#===================================================================================

#获取
def GetImage(bro):
    # save_screenshot 就是将当前页面进行截图且保存
    bro.save_screenshot('taobao.png')

    code_img_ele = bro.find_element_by_xpath("//*[@id='nc_1__scale_text']/span")
    location = code_img_ele.location  #验证码图片左上角的坐标 x,y
    size = code_img_ele.size  # 验证码的标签对应的长和宽
    # 左上角和右下角的坐标
    rangle = (
        int(location['x']),int(location['y']),int(location['x'] + size['width']),int(location['y'] + size['height'])
    )

    i = Image.open("./taobao.png")
    # code_img_name = './tb.png'
    # crop裁剪
    frame = i.crop(rangle)
    # frame.save(code_img_name)

    Action(bro,code_img_ele)

#===================================================================================

#执行
def Action(bro,code_img_ele):
    # 动作链
    action = ActionChains(bro)
    # 长按且点击
    action.click_and_hold(code_img_ele)

    # move_by_offset(x,y) x水平方向,y竖直方向
    # perform()让动作链立即执行
    action.move_by_offset(300, 0).perform()
    time.sleep(0.5)

    # 释放动作链
    action.release()
    # 登录
    bro.find_element_by_xpath("//*[@id='login-form']/div[4]/button").click()
    time.sleep(10)
    bro.quit() #关闭浏览器

if __name__ == "__main__":
    main()