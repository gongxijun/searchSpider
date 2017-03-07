#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import socket
import codecs
# 设置超时
import urlparse
import re
import os
import time
import argparse
import threading
import sys
import proxy
import requests
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')
maxImageNum = 50
download = 30
timeout = 15
socket.setdefaulttimeout(timeout)
type_image = {'jpg', 'jpeg', 'png'}


class HaoSuoSpider:
    # 睡眠时长
    __amount = 0
    __start_amount = 0
    __counter = 0

    def __init__(self, totalPageNum=1, image_path='/data2/xijun.gong/jd_image_data'):
        """
        :param totalPageNum: 下载页数
        :param image_path: 图片放置目录
        """
        self.download = download;
        self.proxy_new = proxy.Proxy()
        self.image_path = image_path
        self.__amount = totalPageNum * maxImageNum + self.__start_amount
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
            'Qunar-App': 'SQxTLo6t4k5HSnsykL7nuz9jL/2FvrM9QfppVEbOhQYxIS5tR6I/w3GIq9wpZLbur3Hw7W//Ec+nFnorxB7gTlSSND1Xrbaj3zmRkWAZUaiRm+djpINDhvsYOXlFZHlrQ0BPZ+uZRIn5xnSAfPTpW1xJehqHDr1769Xs0Ly8rZM='
        }

    def parseJson(self, data, _key='objURL'):
        img_list = []
        _indx = 0;
        while len(data) > 2 and _indx != -1:
            _indx = data.find(_key);
            data = data[_indx:];
            url_tag_index = data.find(',');
            if url_tag_index != -1:
                value = data[:url_tag_index];
                url = value.split('":"')[-1].strip('"');
                img_list.append(url.replace("\/", "/"));
                data = data[url_tag_index + 1:]
        return img_list;

    def __getImg(self, sub_dest_dir, word='dame', extra_word='provice'):
        """
        :param word:搜索的关键字
        """
        _keyword = extra_word.encode('utf-8') + ' ' + word.encode('utf-8');
        # print _keyword;
        search = urllib.pathname2url(str(_keyword))
        # pn int 图片数
        pn = self.__start_amount
        root_path = os.path.join(self.image_path, sub_dest_dir);
        print root_path
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        # 判断名字是否重复，获取图片长度
        self.__counter = len(os.listdir(root_path)) + 1
        while pn <= self.__amount and self.__counter <= self.__amount:
            url = 'http://image.so.com/j?q=' + search + '&src=srp&correct=' + search + '&rn=' + str(
                maxImageNum) + '&sn=' + str(pn) + '&pn=' + str(maxImageNum);
            # page = None
            try:
                proxy = urllib2.ProxyHandler(self.proxy_new.getProxyByTxt())
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener);
                _text = urllib2.Request(url, headers=self.headers);
                data = urllib2.urlopen(_text, timeout=50).read();
                # page = urllib2.urlopen(req)
                # req = urllib2.Request(url=url, headers=self.headers)
                # data = page.read();

                self.__saveImage(root_path, self.parseJson(data=data, _key="\"thumb_bak\":"), word)
                pn += maxImageNum
            except Exception as e:
                print '下载图片异常:', e, url
            finally:
                self.__counter = len(os.listdir(root_path)) + 1
                # if page is not None:
                #     page.close()
        print "下载图片:", word + " 结束"
        pass

    def __saveImage(self, root_path, json, keyWord):
        for info in json:

            try:
                flag_status = 5;
                while flag_status > 0:
                    status_dowm = self.__loadImage(root_path, info);
                    if status_dowm != 00:
                        if status_dowm < 0:
                            print '第' + str(5 - flag_status) + '次下载', str(
                                self.__counter) + "张" + keyWord, '失败', info
                        else:
                            print '文件以存在'
                        flag_status -= 1;
                        continue
                    break;
                if flag_status < 1:
                    continue;
            except Exception, e:
                print e
            self.__counter += 1
            if self.__counter > self.download:
                return

            print str(self.__counter) + "张" + keyWord
        return

    def __loadImage(self, root_path, info):
        prefix = self.__getPrefix(info)
        file_path = os.path.join(root_path, self.__getSuffix(prefix));
        if (os.path.exists(file_path)):
            return 1;
        try:
            #text = self.proxy_new.getProxyByTxt()
            proxy = urllib2.ProxyHandler(self.proxy_new.getProxyByTxt())
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener);
            _text = urllib2.Request(info, headers=self.headers);
            r = urllib2.urlopen(_text, timeout=50).read();
            import codecs
            with codecs.open(file_path, "wb") as code:
                code.write(r)
        except Exception, e:
            print e
            return -1;
        return 0

    def __getSuffix(self, name):
        """
        :param name: 图片uri
        :return: 图片类型
        """
        _type = '.jpg';
        m = re.search(r'\.[^\.]*$', name)
        if m != None and m.group(0) in type_image:
            _type = m.group(0)
        return name.split('.')[0] + _type;

    def __getPrefix(self, name):
        """
        获取url图片中的前缀
        :param name: 图片uri
        :return: 图片名
        """
        return name.split('/')[-1]

    def _Main(self, start, stride, config_path, index_page=1):
        self.__start_amount = (index_page - 1) * maxImageNum
        _index = 0;
        for reader in codecs.open(config_path, 'r', encoding='utf-8'):
            _index += 1;
            ##"避免线程碰撞"
            if _index < start:
                continue;
            else:
                start += stride;
            arr_jd = reader.strip('\n').split('#');
            city = arr_jd[0].split('/');
            if (len(city) < 3):
                print '异常', arr_jd;

            self.__getImg(arr_jd[0], city[-1], extra_word=city[1])


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='spider the web picture and recognition')

    parser.add_argument('--config_path', dest='config_path',
                        help='input the path that config dir',
                        default='profile.txt', type=str, nargs='?')
    parser.add_argument('--stride', dest='stride', help='input the num that you want the size ',
                        default=10, type=int, nargs='?')
    parser.add_argument('--dest_dir', dest='dest_dir', help='input the path-dir that you want to save ',
                        default='/data2/xijun.gong/jd_image_data', type=str, nargs='?')
    args = parser.parse_args()
    return args


def total_main():
    args = parse_args()
    _index = 0
    _thread_Image = [0] * args.stride
    while (_index < args.stride):
        spider = HaoSuoSpider(image_path=args.dest_dir)
        _thread_Image[_index] = threading.Thread(target=spider._Main,
                                                 args=(_index, args.stride, args.config_path, 1))
        _thread_Image[_index].start();
        _index += 1;


if __name__ == '__main__':
    # total_main()
    args = parse_args()
    spider = HaoSuoSpider(image_path='.')
    spider._Main(1, args.stride, args.config_path, 1);
