#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 20:58:56 2016

@author: Zhuolin
"""

import logging
import threading
import PyCTP

logger = logging.getLogger(__name__)

class PyCTP_Market_API(PyCTP.CThostFtdcMdApi):
    """ CTP行情API """
    
    TIMEOUT = 30
    __RequestID = 0
    __isLogined = False
    __SubMarketDataInstrumentID = set()
    
    def __IncRequestID(self):
        """ 自增并返回请求ID """
        #self.__RequestID += 1
        return self.__RequestID
    
    def Connect(self, frontAddr):
        """ 连接前置服务器 """
        self.RegisterSpi(self)
        self.RegisterFront(frontAddr)
        self.Init()
        self.__rsp_Connect = dict(event=threading.Event())
        self.__rsp_Connect['event'].clear()
        return 0 if self.__rsp_Connect['event'].wait(self.TIMEOUT) else -4
        
    def Login(self, BrokerID, UserID, Password):
        """ 用户登录请求 """
        reqUserLogin = dict(BrokerID = BrokerID, UserID = UserID, Password = Password)
        self.__rsp_Login = dict(event = threading.Event(), RequestID = self.__IncRequestID())
        ret = self.ReqUserLogin(reqUserLogin, self.__rsp_Login['RequestID'])
        if ret == 0:
            self.__rsp_Login['event'].clear()
            if self.__rsp_Login['event'].wait(self.TIMEOUT):
                if self.__rsp_Login['ErrorID'] != 0:
                    logger.error('%s' % str(self.__rsp_Login['ErrorMsg'], encoding='gbk'))
                    return self.__rsp_Login['ErrorID']
                self.__isLogined = True
                self.__BrokerID = BrokerID
                self.__UserID = UserID
                self.__Password = Password
                return self.__rsp_Login['result']
            else:
                return -4
        return ret
        
    def Logout(self):
        """ 登出请求 """
        if not self.__isLogined:
            return 6
        reqUserLogout = dict(BrokerID = self.__BrokerID, UserID = self.__UserID)
        self.__rsp_Logout = dict(event = threading.Event(), RequestID = self.__IncRequestID())
        ret = self.ReqUserLogout(reqUserLogout, self.__rsp_Logout['RequestID'])
        if ret == 0:
            self.__rsp_Logout['event'].clear()
            if self.__rsp_Logout['event'].wait(self.TIMEOUT):
                if self.__rsp_Logout['ErrorID'] != 0:
                    return self.__rsp_Logout['ErrorID']
                self.__isLogined = False
                return self.__rsp_Logout['result']
            else:
                return -4
        return ret
        
    def SubMarketData(self, InstrumentID):
        """ 订阅行情 """
        self.__rsp_SubMarketData = dict(results=[], ErrorID=0, event=threading.Event(), RequestID=self.__IncRequestID())
        ret = self.SubscribeMarketData(InstrumentID, len(InstrumentID))
        if ret == 0:
            self.__rsp_SubMarketData['event'].clear()
            if self.__rsp_SubMarketData['event'].wait(self.TIMEOUT):
                if self.__rsp_SubMarketData['ErrorID'] != 0:
                    return self.__rsp_SubMarketData['ErrorID']
                for SpecificInstrument in self.__rsp_SubMarketData['results']:
                    self.__SubMarketDataInstrumentID.add(SpecificInstrument['InstrumentID'])
                    logger.info('CThostFtdcMdApi.SubscribeMarketData(%s)' % SpecificInstrument['InstrumentID'])
                #logger.info('CThostFtdcMdApi.__SubMarketDataInstrumentID= %s' % list(self.__SubMarketDataInstrumentID))
                return self.__rsp_SubMarketData['results']
            else:
                return -4
        return ret
        
    def UnSubMarketData(self, InstrumentID):
        """ 退订行情 """
        self.__rsp_UnSubMarketData = dict(results=[], ErrorID=0, event=threading.Event(), RequestID=self.__IncRequestID())
        ret = self.UnSubscribeMarketData(InstrumentID, len(InstrumentID))
        if ret == 0:
            self.__rsp_UnSubMarketData['event'].clear()
            if self.__rsp_UnSubMarketData['event'].wait(self.TIMEOUT):
                if self.__rsp_UnSubMarketData['ErrorID'] != 0:
                    return self.__rsp_UnSubMarketData['ErrorID']
                for SpecificInstrument in self.__rsp_UnSubMarketData['results']:
                    self.__SubMarketDataInstrumentID.remove(SpecificInstrument['InstrumentID'])
                    logger.info('CThostFtdcMdApi.UnSubscribeMarketData(%s)' % SpecificInstrument['InstrumentID'])
                #logger.info('CThostFtdcMdApi.__SubMarketDataInstrumentID= %s' % list(self.__SubMarketDataInstrumentID))
                return self.__rsp_UnSubMarketData['results']
            else:
                return -4
        return ret
        
    def OnFrontConnected(self):
        """ 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。 """
        logger.info('CThostFtdcMdApi::OnFrontConnected()')
        self.__rsp_Connect['event'].set()
        #if self.__isLogined:
        #    sys.stderr.write('CThostFtdcMdApi::ReqUserLogin... \n')
        #    result = self.Login(self.__BrokerID, self.__UserID, self.__Password)
        #    sys.stderr.write('CThostFtdcMdApi::SubscribeMarketData... \n')
        #    self.SubMarketData(list(self.__SubMarketDataInstrumentID))
            
    def OnFrontDisconnected(self, nReason):
        """ 当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
        nReason 错误原因
        0x1001 网络读失败
        0x1002 网络写失败
        0x2001 接收心跳超时
        0x2002 发送心跳失败
        0x2003 收到错误报文
        """
        logger.warn('CThostFtdcMdApi::OnFrontDisconnected(%s)' % hex(nReason))
        
    def OnRspError(self, RspInfo,  RequestID, IsLast):
        """ 错误信息 """
        logger.error('%s' % repr(('OnRspError', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gbk')], RequestID, IsLast)))
        
    def OnRspUserLogin(self, RspUserLogin, RspInfo, RequestID, IsLast):
        """ 登录请求响应 """
        if RequestID == self.__rsp_Login['RequestID'] and IsLast:
            self.__rsp_Login['result'] = RspUserLogin
            self.__rsp_Login.update(RspInfo)
            self.__rsp_Login['event'].set()
            
    def OnRspUserLogout(self, RspUserLogout, RspInfo, RequestID, IsLast):
        """ 登出请求响应 """
        if RequestID == self.__rsp_Logout['RequestID'] and IsLast:
            self.__rsp_Logout['result'] = RspUserLogout
            self.__rsp_Logout.update(RspInfo)
            self.__rsp_Logout['event'].set()
            
    def OnRspSubMarketData(self, SpecificInstrument, RspInfo, RequestID, IsLast):
        """ 订阅行情应答 """
        if RequestID == self.__rsp_SubMarketData['RequestID']:
            if RspInfo is not None:
                self.__rsp_SubMarketData.update(RspInfo)
            if SpecificInstrument is not None:
                self.__rsp_SubMarketData['results'].append(SpecificInstrument)
            if IsLast:
                self.__rsp_SubMarketData['event'].set()
                
    def OnRspUnSubMarketData(self, SpecificInstrument, RspInfo, RequestID, IsLast):
        """ 取消订阅行情应答 """
        if RequestID == self.__rsp_UnSubMarketData['RequestID']:
            if RspInfo is not None:
                self.__rsp_UnSubMarketData.update(RspInfo)
            if SpecificInstrument is not None:
                self.__rsp_UnSubMarketData['results'].append(SpecificInstrument)
            if IsLast:
                self.__rsp_UnSubMarketData['event'].set()
                
    def OnRtnDepthMarketData(self, DepthMarketData):
        """ 行情推送 """
        logger.info('CThostFtdcMdApi::OnRtnDepthMarketData( %s )' % repr(DepthMarketData) )
        
class PyCTP_Market(PyCTP_Market_API):
    pass
