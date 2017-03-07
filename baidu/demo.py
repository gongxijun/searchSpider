#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import urllib2
import urllib
import json
import socket
# 设置超时
import time

maxImageNum = 80
timeout = 12
socket.setdefaulttimeout(timeout)


class BaiduSpider:
    # 睡眠时长
    __amount = 0
    __start_amount = 0
    __counter = 0

    def __init__(self, totalPageNum=1, image_path='/data2/xijun.gong/jd_image_data'):
        """
        :param totalPageNum: 下载页数
        :param image_path: 图片放置目录
        """
        self.image_path = image_path
        self.__amount = totalPageNum * maxImageNum + self.__start_amount
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'}

    def __getImg(self, word='dame'):
        """
        :param word:搜索的关键字
        """
        search = urllib.pathname2url(word)
        # pn int 图片数
        pn = self.__start_amount
        while pn < self.__amount:
            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' + search + '&cg=girl&pn=' + str(
                pn) + '&rn=' + str(maxImageNum) + '&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'

            try:
                url = "http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&word=花&pn=0&rn=50&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e"
                req = urllib2.Request(url=url, headers=self.headers)
                page = urllib2.urlopen(req)
                data = page.read().decode('utf8')
                # 解析json
                json_data = json.loads(data)
                self.__saveImage(json_data, word)
                pn += maxImageNum
            except Exception as e:
                print '下载图片异常:', e, url
            finally:
                page.close()
        print("下载图片:", word + " 结束")
        pass

    # 保存图片
    def __saveImage(self, json, keyWord):

        if not os.path.exists(os.path.join(self.image_path, keyWord)):
            os.mkdir(os.path.join(self.image_path, keyWord))
        # 判断名字是否重复，获取图片长度
        self.__counter = len(os.listdir(os.path.join(self.image_path, keyWord))) + 1
        for info in json['imgs']:
            try:
                if not self.__downloadImage(info, keyWord):
                    self.__counter -= 1
            except urllib2.HTTPError as urllib_err:
                print(urllib_err)
                pass
            except Exception as err:
                time.sleep(1)
                print(err);
                print("产生未知错误，放弃保存")
                continue
            finally:
                print(str(self.__counter) + "张" + keyWord)
                self.__counter += 1
        return

    # 下载图片
    def __downloadImage(self, info, keyWord):
        suffix = self.__getSuffix(info['objURL'])
        urllib.urlretrieve(info['objURL'],
                           os.path.join(
                               os.path.join(self.image_path, keyWord), str(self.__counter) + str(suffix)))
        return True

    def __getSuffix(self, name):
        """
        :param name: 图片uri
        :return: 图片类型
        """
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpeg'

    def __getPrefix(self, name):
        """
        获取url图片中的前缀
        :param name: 图片uri
        :return: 图片名
        """
        return name[:name.find('.')]

    def _Main(self, keyWord, index_page=1):
        self.__start_amount = (index_page - 1) * maxImageNum
        self.__getImg(keyWord)


if __name__ == '__main__':
    spider = BaiduSpider(image_path='.', totalPageNum=3)
    spider._Main('花', 1)
