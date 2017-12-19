#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 20:58:56 2016

@author: Zhuolin
"""

if __name__ == '__main__':
    import time, os
    from os.path import join, split, dirname, exists
    from PyCTP_Market import PyCTP_Market
    os.makedirs('tmp', exist_ok=True)
    market = PyCTP_Market.CreateFtdcMdApi( join(b'tmp', b'test_m_') )
    time.sleep(1.0)
    #print('连接前置服务器:', market.Connect(b'tcp://180.168.146.187:10031'))
    print('连接前置服务器:', market.Connect(b'tcp://180.168.146.187:10010'))
    time.sleep(1.0)
    print('登陆:', market.Login(b'9999', bytes(input('enter username:'), 'gbk'), bytes(input('enter password:'), 'gbk')))
    time.sleep(1.0)
    print('订阅行情:', market.SubMarketData([b'rb1701', b'rb1702']))
    while input('enter q to quit this program:') is not 'q':
        pass
    time.sleep(1.0)
    print('退订行情:', market.UnSubMarketData([b'rb1701', b'rb1702']))
    time.sleep(1.0)
    print('登出:', market.Logout())