#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Ye
@file: zhubajie.py
@time: 2024/10/22

多页爬取功能尚未实现。其实多页只要把url变成pi即可
"""
import re
import time
import base64
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import numpy as np
from src import captcha
from lxml import etree
cap = captcha.TextSelectCaptcha()
def verify(url):
    content = requests.get(url).content
    # 送入模型识别
    plan = cap.run(content)
    return plan

def sample_from_chaotic_distribution(a, b):
    # 随机选择一个分布
    distribution = random.choice(['uniform', 'normal', 'exponential'])

    if distribution == 'uniform':
        # 从均匀分布中采样
        number = random.uniform(a, b)
    elif distribution == 'normal':
        # 从高斯分布中采样，均值为1.5，标准差为0.5
        mean = (a+b)/2
        std_dev = 0.5
        while True:
            number = random.gauss(mean, std_dev)
            if a <= number <= b:
                break
    elif distribution == 'exponential':
        # 从指数分布中采样，尺度参数为1
        scale = 1
        while True:
            number = np.random.exponential(scale)
            if a <= number <= b:
                break
    return number
ua_list = [ # user-agent
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36Chrome 17.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0Firefox 4.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',  ## 这个header才行
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    ]


headers ={
     # "User-Agent": random.choice(ua_list)
    "User-Agent": 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
 }
class ZBJ(object): # 名字修改   加载webdriver的时候会卡顿，问题原因不清楚
    def __init__(self):
        chrome_options = self.options()
        self.browser = webdriver.Chrome(options=chrome_options)
        # self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 30)
        # self.url = "https://www.zbj.com/fw/xcxkfzbjzbj/"


    # def __del__(self):
    #     self.browser.close()

    def options(self):
        chrome_options = webdriver.ChromeOptions()
        return chrome_options

    def click(self, xpath):
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).click()

    def get_location(self, element):
        rect = element.rect
        center_x = int(rect['x'] - 50)
        center_y = int(rect['y'])
        return center_x, center_y

    def zbj(self):
        url = "https://www.zbj.com/fw/xcxkfzbjzbj/"
        self.browser.get(url)
        time.sleep(3)
        self.browser.refresh()
        sleeptime = sample_from_chaotic_distribution(0,3)
        time.sleep(sleeptime)
        xpath = '//*[@class="geetest_item_wrap"]'
        logo = self.wait.until(EC.presence_of_element_located(
        (By.XPATH, xpath)))
        # 获取图片路径
        f = logo.get_attribute('style')
        url = re.findall('url\("(.+?)"\);', f)
        print(url)
        if url:
            url = url[0]
            print(url)
            #送入模型识别
            plan = verify(url)
            # 获取验证码坐标
            X, Y = self.get_location(logo)
            print(X, Y)
            # 前端展示对于原图的缩放比例
            # 306 * 343
            # 344 *384
            lan_x = 306/306
            lan_y = 343/384
            # lan_x = lan_y = 1
            # ActionChains(self.browser).move_by_offset(X, Y).click().perform()
            # time.sleep(11111)
            for crop in plan:
                x1, y1, x2, y2 = crop
                x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                print(x, y)
                offset_x = 40
                x = x + offset_x
                ActionChains(self.browser).move_by_offset(X + x*lan_x, Y + y*lan_y).click().perform()
                ActionChains(self.browser).move_by_offset(-(X + x*lan_x), -(Y + y*lan_y)).perform()  # 将鼠标位置恢复到移动前
                sleeptime = sample_from_chaotic_distribution(0, 2)
                time.sleep(sleeptime)
            # time.sleep(1000)
            xpath = "/html/body/div[2]/div[2]/div[6]/div/div/div[3]/a/div"
            self.click(xpath)
            time.sleep(5)  # 等待页面刷新
            # 滑到页面底部
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleeptime = sample_from_chaotic_distribution(1,3)
            time.sleep(sleeptime)
            try:
                # 获取并打印当前页面的URL
                current_url = self.browser.current_url
                print("当前页面的URL是:", current_url)
                r = requests.get(current_url, headers=headers, timeout=10, ) #请求页面源代码
                r.raise_for_status()  # 检查是否成功获取
                r.encoding = 'utf-8'
                print(r.text)
                et = etree.HTML(r.text)
                divs = et.xpath('//*[@id="__layout"]/div/div[3]/div[1]/div[4]/div/div[2]/div/div[2]/div')
                result = []  # 字典列表
                for div in divs:
                    # 商品价格
                    price = div.xpath('./div[1]/div[3]/div[1]/span/text()')
                    # print(price)
                    if not price:
                        continue
                    server = div.xpath('./div[1]/div[5]/div[1]/div[1]/div[@class="shop-info text-overflow-line"]/text()')

                    goods_name = div.xpath('./div[1]/div[3]/div[2]/a/span/text()')


                    parsed_product = {
                        '商品名': goods_name,
                        '服务商': server,
                        "价格": price
                    }

                    print(parsed_product)

                    result.append(parsed_product)
                return result
            except Exception as e:
                print(f"发生未知错误：{e}")



        else:
            print("error: 未获得到验证码地址")
            # draw(content, res)
            return





if __name__ == '__main__':
    bj = ZBJ()
    results = bj.zbj()

    filename = 'zhubajie.csv'  # 要将数据存到的文件名
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        """
        csv.DictWriter 是 csv 模块中的一个类，专门用于将字典数据写入 CSV 文件。每一行会将字典的键作为 CSV 文件的列名。
        file 是文件对象，fieldnames 是一个列表，指定了 CSV 文件中的列名（或表头），这些列名应该与字典中的键匹配。
        这里的列名是：'品名', '最低价', '最高价', '平均价', '规格', '产地', '单位', '发布日期'，这表示每个产品的这些属性将会被写入 CSV 文件的相应列中。
        """

        writer = csv.DictWriter(file, fieldnames=[
            '商品名', '服务商', "价格"
        ])

        """
        writer.writeheader() 会在文件中写入一行，内容是 fieldnames 中指定的列名，作为 CSV 文件的表头。这一行将成为 CSV 文件的第一行。
        """

        writer.writeheader()  # 写入表头


        for result in results:
            writer.writerow(result)  # 写入每一行数据
    print("所有数据处理完成")
