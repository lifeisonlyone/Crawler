from selenium import webdriver
from urllib.parse import quote, unquote
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

import time


#浏览器配置信息
USER_DIR=r"C:\Users\小胖\AppData\Local\Google\Chrome\User Data"
# TODO 配置代理


class Taobao:
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        #ids =['103.116.113.62:8888']
        #chrome_option.add_argument(f'--proxy-server=http://{ids}')

        chrome_option.add_argument("disable-blink-features=AutomationControlled")
        #绕过登录反爬机制
        chrome_option.add_argument("--user-data-dir={}".format(USER_DIR))

        self.browser = webdriver.Chrome( chrome_options=chrome_option)
        with open("stealth.min.js", "r", encoding="utf-8") as f:
            js_code = f.read()
        #防止selenium被认出来,隐藏其特征
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js_code
        })

    def search(self, keyword):

        #找到搜索框并输入文字
        input = self.browser.find_element_by_css_selector("input[aria-label='请输入搜索文字']")
        input.send_keys(keyword)
        #找到搜索按钮并执行
        search_button = self.browser.find_element_by_css_selector("button[class='btn-search tb-bg']")
        search_button.click()

    def search_condition(self):
        sort = self.browser.find_element_by_css_selector("a[data-value='sale-desc']")
        sort.click()

    def parse(self, html):
        result = []
        soup = BeautifulSoup(html, 'lxml')
        itemlist = soup.select("div[class^='item J_MouserOnverReq']")
        for item in itemlist:
            # 不会报错是有隐患, 因为你不知道当前页面是否真的有值
            title = item.select("div[class^='row row-2 title']")[0].text.strip()
            # TODO 完成解析
            result.append([title])

        return result

    def pipeline(self, item_list):
        # TODO 完成存入数据库
        for item in item_list:
            print(item)

    def click_next_page(self):
        next_page = self.browser.find_element_by_css_selector("li[class='item next']")
        next_page.click()

    def pass_slide(self):
        # 定位验证码所在iframe环境
        iframe = self.browser.find_element_by_css_selector("iframe[src*='punish']")
        # 切换至该iframe环境
        self.browser.switch_to.frame(iframe)
        slide = self.browser.find_element_by_css_selector("#nc_1_n1z")
        ActionChains(self.browser).click_and_hold(slide).move_by_offset(300, 0).perform()
        # 切回主环境
        self.browser.switch_to.window(self.browser.window_handles[0])
        # 重新点击下一页
    def pass_slide2(self):
        print('rr')
        # 定位验证码所在iframe环境
        iframe2  = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
        # 切换至该iframe环境
      #  self.browser.switch_to.frame(iframe)
        slide = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
        ActionChains(self.browser).click_and_hold(slide).move_by_offset(300, 0).perform()
        # 切回主环境
       # self.browser.switch_to.window(self.browser.window_handles[0])
        # 重新点击下一页
    def check_slide(self):
        try:
            iframe = self.browser.find_element_by_css_selector("iframe[src*='punish']")
            return True
        except NoSuchElementException:
            return False



    def check_slide2(self):
        try:
            iframe2  = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
            print('23')
            return True
        except NoSuchElementException:
            return False

    def main(self, keyword_array):
        try:
            for keyword in keyword_array:
                # 加载首页
                index_url = "https://taobao.com"
                self.browser.get(index_url)
                # 模拟搜索
                self.search(keyword)
                time.sleep(2)

                if '验证码拦截' in self.browser.page_source:
                    whether_slide2 = self.check_slide2()
                    if whether_slide2:
                        time.sleep(3)
                        self.pass_slide2()
                # 模拟设置搜索条件
                self.search_condition()
                # 总体浏览一遍当前页面
                ActionChains(self.browser).send_keys(Keys.END).perform()
                ActionChains(self.browser).send_keys(Keys.HOME).perform()
                for page_num in range(1, 6):
                    if page_num == 1:
                        result = self.parse(self.browser.page_source)
                        self.pipeline(result)
                    self.click_next_page()
                    whether_slide = self.check_slide()
                    if whether_slide:
                        time.sleep(3)
                        self.pass_slide()
                        # 如果点击下一页仍出现验证码, 说明已被反爬, 需要更换IP
                        self.click_next_page()
                        time.sleep(1)

                        # 如果点击下一页仍出现验证码, 说明已被反爬, 需要更换IP

                    time.sleep(4)
        except  Exception  as  e:

            print(e)




if __name__ == "__main__":
    keyword_array = ["键盘", "鼠标", "显卡", "音响", "耳机", "硬盘"]
    taobao = Taobao()
    taobao.main(keyword_array)