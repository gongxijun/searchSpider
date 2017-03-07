#!/usr/bin/env python
# encoding=utf8
import urllib2
import urllib
from  bs4 import BeautifulSoup
import sys
import os
import random
import requests


class Proxy:
    def __init__(self):
        self.init_url = 'http://www.xicidaili.com/nn/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'}
        pass

    def getProxy(self):
        url_page = 5
        _proxie = self.getProxyByTxt()
        while True:
            try:
                url = os.path.join(self.init_url, str(url_page))
                print _proxie
                res = requests.get(url=url, proxies=_proxie, timeout=2, headers=self.headers)
                html = res.text
                soup = BeautifulSoup(html, 'html.parser')
                ips = soup.findAll('tr')
                f = open("proxy.txt", "a+")
                cnt_ip = 0
                for x in range(1, len(ips)):
                    ip = ips[x]
                    tds = ip.findAll("td")
                    ip_temp = tds[1].contents[0] + "\t" + tds[2].contents[0] + "\n"
                    # print tds[2].contents[0]+"\t"+tds[3].contents[0]
                    f.write(ip_temp)
                    cnt_ip = x
                f.close()
                url_page += 1
                if cnt_ip < 1:
                    break
            except Exception, e:
                _proxie = self.getProxyByTxt()
                print e
                pass

    def getProxyByTxt(self):
      with open("proxy") as f:
        lines = f.readlines()
        proxys = []
        for i in range(0, len(lines)):
            ip = lines[i].strip("\n").split("\t")
            proxy_host = ip[0] + ":" + ip[1]
            proxy_temp = {"http": proxy_host}
            proxys.append(proxy_temp)
      random_num = 0  # random.randint(0, len(proxys))
      return proxys[random_num]


if __name__ == '__main__':
    _proxy = Proxy()
    _proxy.getProxy()

