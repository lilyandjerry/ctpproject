# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 21:48:07 2016

@author: Zhuolin
"""

import logging
import threading
import PyCTP

logger = logging.getLogger(__name__)

class PyCTP_Trader_API(PyCTP.CThostFtdcTraderApi):
    
    TIMEOUT = 30
    __RequestID = 0
    __isLogined = False
    
    def __IncRequestID(self):
        """ 自增并返回请求ID """
        self.__RequestID += 1
        return self.__RequestID
    
    def __IncOrderRef(self):
        """ 递增报单引用 """
        OrderRef = bytes('%012d' % self.__OrderRef, 'gbk')
        self.__OrderRef += 1
        return OrderRef
        
    def setInvestorID(self, InvestorID):
        self.__InvestorID = InvestorID
        return self.__InvestorID
        
    def Connect(self, frontAddr):
        """ 连接前置服务器 """
        self.RegisterSpi(self)
        self.SubscribePrivateTopic(PyCTP.THOST_TERT_RESTART)
        self.SubscribePublicTopic(PyCTP.THOST_TERT_RESTART)
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
                self.__Password = Password
                self.__BrokerID = self.__rsp_Login['result']['BrokerID']
                self.__UserID = self.__rsp_Login['result']['UserID']
                self.__SystemName = self.__rsp_Login['result']['SystemName']
                self.__TradingDay = self.__rsp_Login['result']['TradingDay']
                self.__DCETime = self.__rsp_Login['result']['DCETime']
                self.__SessionID = self.__rsp_Login['result']['SessionID'] 
                self.__MaxOrderRef = self.__rsp_Login['result']['MaxOrderRef']
                self.__OrderRef = int(self.__MaxOrderRef) # 初始化报单引用
                self.__INETime = self.__rsp_Login['result']['INETime']
                self.__LoginTime = self.__rsp_Login['result']['LoginTime']
                self.__FrontID = self.__rsp_Login['result']['FrontID']
                self.__FFEXTime = self.__rsp_Login['result']['FFEXTime']
                self.__CZCETime = self.__rsp_Login['result']['CZCETime']
                self.__SHFETime = self.__rsp_Login['result']['SHFETime']
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
        
    def QryInstrument(self, ExchangeID=b'', InstrumentID=b''):
        """ 查询和约 """
        QryInstrument = dict(ExchangeID = ExchangeID, InstrumentID  = InstrumentID)
        self.__rsp_QryInstrument = dict(event = threading.Event(),
                                        RequestID = self.__IncRequestID(),
                                        results = [],
                                        ErrorID = 0)
        ret = self.ReqQryInstrument(QryInstrument, self.__rsp_QryInstrument['RequestID'])
        if ret == 0:
            self.__rsp_QryInstrument['event'].clear()
            if self.__rsp_QryInstrument['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInstrument['ErrorID'] != 0:
                    return self.__rsp_QryInstrument['ErrorID']
                return self.__rsp_QryInstrument['results']
            else:
                return -4
        return ret
        
    def QryInstrumentMarginRate(self, InstrumentID):
        """ 请求查询合约保证金率 """
        QryInstrumentMarginRate = dict(BrokerID = self.__BrokerID, InvestorID = self.__InvestorID, InstrumentID = InstrumentID)
        self.__rsp_QryInstrumentMarginRate = dict(results =  [],
                                                  RequestID = self.__IncRequestID(),
                                                  ErrorID = 0,
                                                  event = threading.Event())
        ret = self.ReqQryInstrumentMarginRate(QryInstrumentMarginRate, self.__rsp_QryInstrumentMarginRate['RequestID'])
        if ret == 0:
            self.__rsp_QryInstrumentMarginRate['event'].clear()
            if self.__rsp_QryInstrumentMarginRate['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInstrumentMarginRate['ErrorID'] != 0:
                    return self.__rsp_QryInstrumentMarginRate['ErrorID']
                #assert len(self.__rsp_QryInstrumentMarginRate['results']) == 1
                return self.__rsp_QryInstrumentMarginRate['results']
            else:
                return -4
        return ret
        
    def QryInstrumentCommissionRate(self, InstrumentID):
        """ 请求查询合约手续费率 """
        QryInstrumentCommissionRate = dict(BrokerID = self.__BrokerID, InvestorID = self.__InvestorID, InstrumentID = InstrumentID)
        self.__rsp_QryInstrumentCommissionRate = dict(results       =  []
                                                      , RequestID   = self.__IncRequestID()
                                                      , ErrorID     = 0
                                                      , event       = threading.Event())
        ret = self.ReqQryInstrumentCommissionRate(QryInstrumentCommissionRate, self.__rsp_QryInstrumentCommissionRate['RequestID'])
        if ret == 0:
            self.__rsp_QryInstrumentCommissionRate['event'].clear()
            if self.__rsp_QryInstrumentCommissionRate['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInstrumentCommissionRate['ErrorID'] != 0:
                    return self.__rsp_QryInstrumentCommissionRate['ErrorID']
                #assert len(self.__rsp_QryInstrumentCommissionRate['results']) == 1
                return self.__rsp_QryInstrumentCommissionRate['results']
            else:
                return -4
        return ret
    
    def QryInvestorPosition(self, InstrumentID=b''):
        """ 请求查询投资者持仓 """
        QryInvestorPositionFiel = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID)
        self.__rsp_QryInvestorPosition = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryInvestorPosition(QryInvestorPositionFiel, self.__rsp_QryInvestorPosition['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestorPosition['event'].clear()
            if self.__rsp_QryInvestorPosition['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestorPosition['ErrorID'] != 0:
                    return self.__rsp_QryInvestorPosition['ErrorID']
                return self.__rsp_QryInvestorPosition['results']
            else:
                return -4
        return ret
        
    def QryInvestorPositionDetail(self, InstrumentID=b''):
        """ 请求查询投资者持仓明细 """
        QryInvestorPositionDetail = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID)
        self.__rsp_QryInvestorPositionDetail = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryInvestorPositionDetail(QryInvestorPositionDetail, self.__rsp_QryInvestorPositionDetail['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestorPositionDetail['event'].clear()
            if self.__rsp_QryInvestorPositionDetail['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestorPositionDetail['ErrorID'] != 0:
                    return self.__rsp_QryInvestorPositionDetail['ErrorID']
                return self.__rsp_QryInvestorPositionDetail['results']
            else:
                return -4
        return ret
        
    def QryTradingAccount(self):
        """ 请求查询资金账户 """
        QryTradingAccountField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID)
        self.__rsp_QryTradingAccount = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryTradingAccount(QryTradingAccountField, self.__rsp_QryTradingAccount['RequestID'])
        if ret == 0:
            self.__rsp_QryTradingAccount['event'].clear()
            if self.__rsp_QryTradingAccount['event'].wait(self.TIMEOUT):
                if self.__rsp_QryTradingAccount['ErrorID'] != 0:
                    return self.__rsp_QryTradingAccount['ErrorID']
                assert len(self.__rsp_QryTradingAccount['results']) == 1
                return self.__rsp_QryTradingAccount['results'][0]
            else:
                return -4
        return ret
        
    def QryInvestor(self):
        """ 请求查询投资者 """
        InvestorField = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID)
        self.__rsp_QryInvestor = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryInvestor(InvestorField, self.__rsp_QryInvestor['RequestID'])
        if ret == 0:
            self.__rsp_QryInvestor['event'].clear()
            if self.__rsp_QryInvestor['event'].wait(self.TIMEOUT):
                if self.__rsp_QryInvestor['ErrorID'] != 0:
                    return self.__rsp_QryInvestor['ErrorID']
                assert len(self.__rsp_QryInvestor['results']) == 1
                return self.__rsp_QryInvestor['results'][0]
            else:
                return -4
        return ret
        
    def QryExchange(self, ExchangeID=b''):
        """ 请求查询交易所 """
        QryExchangeField = dict(ExchangeID=ExchangeID)
        self.__rsp_QryExchange = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryExchange(QryExchangeField, self.__rsp_QryExchange['RequestID'])
        if ret == 0:
            self.__rsp_QryExchange['event'].clear()
            if self.__rsp_QryExchange['event'].wait(self.TIMEOUT):
                if self.__rsp_QryExchange['ErrorID'] != 0:
                    return self.__rsp_QryExchange['ErrorID']
                return self.__rsp_QryExchange['results']
            else:
                return -4
        return ret
        
    def QrySettlementInfo(self, TradingDay=b''):
        """ 请求查询投资者结算结果 """
        QrySettlementInfo = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, TradingDay=TradingDay)
        self.__rsp_QrySettlementInfo = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQrySettlementInfo(QrySettlementInfo, self.__rsp_QrySettlementInfo['RequestID'])
        if ret == 0:
            self.__rsp_QrySettlementInfo['event'].clear()
            if self.__rsp_QrySettlementInfo['event'].wait(self.TIMEOUT):
                if self.__rsp_QrySettlementInfo['ErrorID'] != 0:
                    return self.__rsp_QrySettlementInfo['ErrorID']
                result = {'Content':b''}
                for item in self.__rsp_QrySettlementInfo['results']:
                    if result.get('TradingDay') is not None:
                        assert result['TradingDay'] == item['TradingDay']
                    if result.get('SettlementID') is not None:
                        assert result['SettlementID'] == item['SettlementID']
                    if result.get('BrokerID') is not None:
                        assert result['BrokerID'] == item['BrokerID']
                    if result.get('InvestorID') is not None:
                        assert result['InvestorID'] == item['InvestorID']
                    if result.get('SequenceNo') is not None:
                        assert result['SequenceNo'] == item['SequenceNo']
                    result['TradingDay'] = item['TradingDay']
                    result['SettlementID'] = item['SettlementID']
                    result['BrokerID'] = item['BrokerID']
                    result['InvestorID'] = item['InvestorID']
                    result['SequenceNo'] = item['SequenceNo']
                    result['Content'] += item['Content']
                return result
            else:
                return -4
        return ret
        
    def QrySettlementInfoConfirm(self):
        """ 请求查询结算信息确认 """
        QrySettlementInfoConfirm = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID)
        self.__rsp_QrySettlementInfoConfirm = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQrySettlementInfoConfirm(QrySettlementInfoConfirm, self.__rsp_QrySettlementInfoConfirm['RequestID'])
        if ret == 0:
            self.__rsp_QrySettlementInfoConfirm['event'].clear()
            if self.__rsp_QrySettlementInfoConfirm['event'].wait(self.TIMEOUT):
                if self.__rsp_QrySettlementInfoConfirm['ErrorID'] != 0:
                    return self.__rsp_QrySettlementInfoConfirm['ErrorID']
                #assert len(self.__rsp_QrySettlementInfoConfirm['results']) == 1
                return self.__rsp_QrySettlementInfoConfirm['results']
            else:
                return -4
        return ret
        
    def SettlementInfoConfirm(self, ConfirmDate=b'', ConfirmTime=b''):
        """ 投资者结算结果确认 """
        SettlementInfoConfirm = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID,
                                     ConfirmDate=ConfirmDate, ConfirmTime=ConfirmTime)
        self.__rsp_SettlementInfoConfirm = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqSettlementInfoConfirm(SettlementInfoConfirm, self.__rsp_SettlementInfoConfirm['RequestID'])
        if ret == 0:
            self.__rsp_SettlementInfoConfirm['event'].clear()
            if self.__rsp_SettlementInfoConfirm['event'].wait(self.TIMEOUT):
                if self.__rsp_SettlementInfoConfirm['ErrorID'] != 0:
                    return self.__rsp_SettlementInfoConfirm['ErrorID']
                #assert len(self.__rsp_SettlementInfoConfirm['results']) == 1
                return self.__rsp_SettlementInfoConfirm['results']
            else:
                return -4
        return ret
        
    def QryDepthMarketData(self, InstrumentID):
        """ 请求查询行情 """
        QryDepthMarketData = dict(InstrumentID=InstrumentID)
        self.__rsp_QryDepthMarketData = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryDepthMarketData(QryDepthMarketData, self.__rsp_QryDepthMarketData['RequestID'])
        if ret == 0:
            self.__rsp_QryDepthMarketData['event'].clear()
            if self.__rsp_QryDepthMarketData['event'].wait(self.TIMEOUT):
                if self.__rsp_QryDepthMarketData['ErrorID'] != 0:
                    return self.__rsp_QryDepthMarketData['ErrorID']
                #assert len(self.__rsp_QryDepthMarketData['results']) == 1
                return self.__rsp_QryDepthMarketData['results']
            else:
                return -4
        return ret
        
    def QryOrder(self, InstrumentID=b'', ExchangeID=b'', OrderSysID=b'', InsertTimeStart=b'', InsertTimeEnd=b''):
        """ 请求查询报单 """
        QryOrder = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID, ExchangeID=ExchangeID, OrderSysID=OrderSysID, InsertTimeStart=InsertTimeStart, InsertTimeEnd=InsertTimeEnd)
        self.__rsp_QryOrder = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryOrder(QryOrder, self.__rsp_QryOrder['RequestID'])
        if ret == 0:
            self.__rsp_QryOrder['event'].clear()
            if self.__rsp_QryOrder['event'].wait(self.TIMEOUT):
                if self.__rsp_QryOrder['ErrorID'] != 0:
                    return self.__rsp_QryOrder['ErrorID']
                return self.__rsp_QryOrder['results']
            else:
                return -4
        return ret
        
    def QryTrade(self, InstrumentID=b'', ExchangeID=b'', TradeID=b'', TradeTimeStart=b'', TradeTimeEnd=b''):
        """ 请求查询成交 """
        QryTrade = dict(BrokerID=self.__BrokerID, InvestorID=self.__InvestorID, InstrumentID=InstrumentID, ExchangeID=ExchangeID, TradeID=TradeID, TradeTimeStart=TradeTimeStart, TradeTimeEnd=TradeTimeEnd)
        self.__rsp_QryTrade = dict(results=[], RequestID=self.__IncRequestID(), ErrorID=0, event=threading.Event())
        ret = self.ReqQryTrade(QryTrade, self.__rsp_QryTrade['RequestID'])
        if ret == 0:
            self.__rsp_QryTrade['event'].clear()
            if self.__rsp_QryTrade['event'].wait(self.TIMEOUT):
                if self.__rsp_QryTrade['ErrorID'] != 0:
                    return self.__rsp_QryTrade['ErrorID']
                return self.__rsp_QryTrade['results']
            else:
                return -4
        return ret
        
    def OrderInsert(self, InstrumentID, Action, Direction, Volume, Price):
        """ 开平仓(限价挂单)申报, 注意,这是异步指令 """
        InputOrder = {}
        InputOrder['BrokerID'] = self.__BrokerID                            # 经纪公司代码
        InputOrder['InvestorID'] = self.__InvestorID                        # 投资者代码
        InputOrder['InstrumentID'] = InstrumentID                           # 合约代码
        InputOrder['OrderRef'] = self.__IncOrderRef()                       # 报单引用
        InputOrder['UserID'] = self.__UserID                                # 用户代码
        InputOrder['OrderPriceType'] = PyCTP.THOST_FTDC_OPT_LimitPrice      # 报单价格条件:限价
        InputOrder['Direction'] = Direction                                 # 买卖方向
        InputOrder['CombOffsetFlag'] = Action                               # 组合开平标志
        InputOrder['CombHedgeFlag']=PyCTP.THOST_FTDC_HF_Speculation         # 组合投机套保标志:投机
        InputOrder['LimitPrice'] = Price                                    # 价格
        InputOrder['VolumeTotalOriginal'] = Volume                          # 数量
        InputOrder['TimeCondition'] = PyCTP.THOST_FTDC_TC_GFD               # 有效期类型:当日有效
        InputOrder['VolumeCondition'] = PyCTP.THOST_FTDC_VC_AV              # 成交量类型:任意数量
        InputOrder['ContingentCondition'] = PyCTP.THOST_FTDC_CC_Immediately # 触发条件:立即
        InputOrder['ForceCloseReason'] = PyCTP.THOST_FTDC_FCC_NotForceClose # 强平原因:非强平
        InputOrder['RequestID'] = self.__IncRequestID()                     # 请求编号
        return self.ReqOrderInsert(InputOrder, InputOrder['RequestID'])
    
    def OrderAction(self, ActionFlag, FrontID, SessionID, OrderRef, ExchangeID, OrderSysID):
        """ 报单操作请求(撤单), 注意,这是异步指令 """
        assert ActionFlag == PyCTP.THOST_FTDC_AF_Delete
        InputOrderAction = {}
        InputOrderAction['BrokerID'] = self.__BrokerID                          # 经纪公司代码
        InputOrderAction['UserID'] = self.__UserID                              # 用户代码
        InputOrderAction['InvestorID'] = self.__InvestorID                      # 投资者代码
        InputOrderAction['OrderActionRef'] = int(self.__IncOrderRef())          # 操作引用
        InputOrderAction['OrderRef'] = OrderRef                                 # 报单引用
        InputOrderAction['RequestID'] = self.__IncRequestID()                   # 请求编号
        InputOrderAction['FrontID'] = FrontID                                   # 前置编号
        InputOrderAction['SessionID'] = SessionID                               # 会话编号
        InputOrderAction['ExchangeID'] = ExchangeID                             # 交易所代码
        InputOrderAction['OrderSysID'] = OrderSysID                             # 报单编号
        InputOrderAction['ActionFlag'] = ActionFlag                             # 操作标志:撤单
        return self.ReqOrderAction(InputOrderAction, InputOrderAction['RequestID'])
        
    def OnRspError(self, RspInfo,  RequestID, IsLast):
        """ 错误信息 """
        logger.error('%s' % repr(('OnRspError', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gbk')], RequestID, IsLast)))
        
    def OnFrontConnected(self):
        """ 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。 """
        logger.info('CThostFtdcTraderApi::OnFrontConnected()')
        self.__rsp_Connect['event'].set()
        #if self.__isLogined:
        #    sys.stderr.write('CThostFtdcTraderApi::ReqUserLogin...')
        #    result = self.Login(self.__BrokerID, self.__UserID, self.__Password)
    
    def OnFrontDisconnected(self, nReason):
        """ 当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
        nReason 错误原因
        0x1001 网络读失败
        0x1002 网络写失败
        0x2001 接收心跳超时
        0x2002 发送心跳失败
        0x2003 收到错误报文
        """
        logger.warn('CThostFtdcTraderApi::OnFrontDisconnected(%s)' % hex(nReason))
        
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
            
    def OnRspQryInstrument(self, Instrument, RspInfo, RequestID, IsLast):
        """ 请求查询合约响应 """
        if RequestID == self.__rsp_QryInstrument['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrument.update(RspInfo)
            if Instrument is not None:
                self.__rsp_QryInstrument['results'].append(Instrument)
            if IsLast:
                self.__rsp_QryInstrument['event'].set()
                
    def OnRspQryInstrumentMarginRate(self, InstrumentMarginRate, RspInfo, RequestID, IsLast):
        """ 请求查询合约保证金率响应 """
        if RequestID == self.__rsp_QryInstrumentMarginRate['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrumentMarginRate.update(RspInfo)
            if InstrumentMarginRate is not None:
                self.__rsp_QryInstrumentMarginRate['results'].append(InstrumentMarginRate)
            if IsLast:
                self.__rsp_QryInstrumentMarginRate['event'].set()
                
    def OnRspQryInstrumentCommissionRate(self, InstrumentCommissionRate, RspInfo, RequestID, IsLast):
        """ 请求查询合约手续费率响应 """
        if RequestID == self.__rsp_QryInstrumentCommissionRate['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInstrumentCommissionRate.update(RspInfo)
            if InstrumentCommissionRate is not None:
                self.__rsp_QryInstrumentCommissionRate['results'].append(InstrumentCommissionRate)
            if IsLast:
                self.__rsp_QryInstrumentCommissionRate['event'].set()
                
    def OnRspQryInvestorPosition(self, InvestorPosition, RspInfo, RequestID, IsLast):
        """ 请求查询投资者持仓响应 """
        if RequestID == self.__rsp_QryInvestorPosition['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestorPosition.update(RspInfo)
            if InvestorPosition is not None:
                self.__rsp_QryInvestorPosition['results'].append(InvestorPosition)
            if IsLast:
                self.__rsp_QryInvestorPosition['event'].set()
    
    def OnRspQryInvestorPositionDetail(self, InvestorPositionDetail, RspInfo, RequestID, IsLast):
        """ 请求查询投资者持仓明细响应 """
        if RequestID == self.__rsp_QryInvestorPositionDetail['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestorPositionDetail.update(RspInfo)
            if InvestorPositionDetail is not None:
                self.__rsp_QryInvestorPositionDetail['results'].append(InvestorPositionDetail)
            if IsLast:
                self.__rsp_QryInvestorPositionDetail['event'].set()
                
    def OnRspQryTradingAccount(self, TradingAccount, RspInfo, RequestID, IsLast):
        """ 请求查询资金账户响应 """
        if RequestID == self.__rsp_QryTradingAccount['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryTradingAccount.update(RspInfo)
            if TradingAccount is not None:
                self.__rsp_QryTradingAccount['results'].append(TradingAccount)
            if IsLast:
                self.__rsp_QryTradingAccount['event'].set()
                
    def OnRspQryInvestor(self, Investor, RspInfo, RequestID, IsLast):
        """ 请求查询投资者响应 """
        if RequestID == self.__rsp_QryInvestor['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryInvestor.update(RspInfo)
            if Investor is not None:
                self.__rsp_QryInvestor['results'].append(Investor)
            if IsLast:
                self.__rsp_QryInvestor['event'].set()
    
    def OnRspQryExchange(self, Exchange, RspInfo, RequestID, IsLast):
        """ 请求查询交易所响应 """
        if RequestID == self.__rsp_QryExchange['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryExchange.update(RspInfo)
            if Exchange is not None:
                self.__rsp_QryExchange['results'].append(Exchange)
            if IsLast:
                self.__rsp_QryExchange['event'].set()
                
    def OnRspQrySettlementInfo(self, SettlementInfo, RspInfo, RequestID, IsLast):
        """ 请求查询投资者结算结果响应 """
        if RequestID == self.__rsp_QrySettlementInfo['RequestID']:
            if RspInfo is not None:
                self.__rsp_QrySettlementInfo.update(RspInfo)
            if SettlementInfo is not None:
                self.__rsp_QrySettlementInfo['results'].append(SettlementInfo)
            if IsLast:
                self.__rsp_QrySettlementInfo['event'].set()
                
    def OnRspQrySettlementInfoConfirm(self, SettlementInfoConfirm, RspInfo, RequestID, IsLast):
        """ 请求查询结算信息确认响应 """
        if RequestID == self.__rsp_QrySettlementInfoConfirm['RequestID']:
            if RspInfo is not None:
                self.__rsp_QrySettlementInfoConfirm.update(RspInfo)
            if SettlementInfoConfirm is not None:
                self.__rsp_QrySettlementInfoConfirm['results'].append(SettlementInfoConfirm)
            if IsLast:
                self.__rsp_QrySettlementInfoConfirm['event'].set()
                
    def OnRspSettlementInfoConfirm(self, SettlementInfoConfirm, RspInfo, RequestID, IsLast):
        """ 请求查询结算信息确认响应 """
        if RequestID == self.__rsp_SettlementInfoConfirm['RequestID']:
            if RspInfo is not None:
                self.__rsp_SettlementInfoConfirm.update(RspInfo)
            if SettlementInfoConfirm is not None:
                self.__rsp_SettlementInfoConfirm['results'].append(SettlementInfoConfirm)
            if IsLast:
                self.__rsp_SettlementInfoConfirm['event'].set()
                
    def OnRspQryDepthMarketData(self, DepthMarketData, RspInfo, RequestID, IsLast):
        """ 请求查询交易所响应 """
        if RequestID == self.__rsp_QryDepthMarketData['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryDepthMarketData.update(RspInfo)
            if DepthMarketData is not None:
                self.__rsp_QryDepthMarketData['results'].append(DepthMarketData)
            if IsLast:
                self.__rsp_QryDepthMarketData['event'].set()
                
    def OnRspQryOrder(self, Order, RspInfo, RequestID, IsLast):
        """ 请求查询报单响应 """
        if RequestID == self.__rsp_QryOrder['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryOrder.update(RspInfo)
            if Order is not None:
                self.__rsp_QryOrder['results'].append(Order)
            if IsLast:
                self.__rsp_QryOrder['event'].set()
                
    def OnRspQryTrade(self, Trade, RspInfo, RequestID, IsLast):
        """ 请求查询成交响应 """
        if RequestID == self.__rsp_QryTrade['RequestID']:
            if RspInfo is not None:
                self.__rsp_QryTrade.update(RspInfo)
            if Trade is not None:
                self.__rsp_QryTrade['results'].append(Trade)
            if IsLast:
                self.__rsp_QryTrade['event'].set()
                
    def OnRspOrderInsert(self, InputOrder, RspInfo, RequestID, IsLast):
        """ 报单录入请求响应 """
        if RspInfo is not None and RspInfo['ErrorID'] != 0:
            logger.info('%s' % repr(('OnRspOrderInsert', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gb2312')], RequestID, IsLast)) )
            
    def OnErrRtnOrderInsert(self, InputOrder, RspInfo):
        """ 报单录入错误回报 """
        if RspInfo is not None and RspInfo['ErrorID'] != 0:
            logger.warn('%s' % repr(('OnErrRtnOrderInsert', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gb2312')] )) )
            
    def OnRspOrderAction(self, InputOrderAction, RspInfo, RequestID, IsLast):
        """ 报单操作请求响应 """
        if RspInfo is not None and RspInfo['ErrorID'] != 0:
            logger.info('%s' % repr(('OnRspOrderAction', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gb2312')], RequestID, IsLast)) )
            
    def OnErrRtnOrderAction(self, OrderAction, RspInfo):
        """ 报单操作错误回报 """
        if RspInfo is not None and RspInfo['ErrorID'] != 0:
            logger.warn('%s' % repr(('OnErrRtnOrderAction', [RspInfo['ErrorID'], str(RspInfo['ErrorMsg'], encoding='gb2312')] )) )
            
    def OnRtnOrder(self, Order):
        """ 报单通知 """
        #print('OnRtnOrder:', Order, file=sys.stderr)
        logger.info('%s' % repr(('OnRtnOrder', Order['InstrumentID'], Order['FrontID'], Order['SessionID'], Order['OrderRef'], Order['ExchangeID'], Order['OrderSysID'], Order['OrderStatus'])) )
        
    def OnRtnTrade(self, Trade):
        """ 成交通知 """
        #print('OnRtnTrade:', Trade, file=sys.stderr)
        logger.info('%s' % repr(('OnRtnTrade', Trade['InstrumentID'], Trade['ExchangeID'], Trade['TradeID'], Trade['OffsetFlag'], Trade['Direction'] )) )
        
    def OnRtnInstrumentStatus(self, InstrumentStatus):
        """ 合约交易状态通知 """
        logger.info('%s' % repr(('OnRtnInstrumentStatus', InstrumentStatus['InstrumentID'],  InstrumentStatus['InstrumentStatus'])))
    
    def OnRtnFromBankToFutureByFuture(self, RspTransfer):
        """ 期货发起银行资金转期货通知 """
        logger.info('%s' % repr(('OnRtnFromBankToFutureByFuture', RspTransfer['TradeAmount'])))
    
    def OnRtnFromFutureToBankByFuture(self, RspTransfer):
        """ 期货发起期货资金转银行通知 """
        logger.info('%s' % repr(('OnRtnFromFutureToBankByFuture', RspTransfer['TradeAmount'])))
        
    def OnRtnCFMMCTradingAccountToken(self, CFMMCTradingAccountToken):
        """ 保证金监控中心用户令牌 """
        logger.info('OnRtnCFMMCTradingAccountToken')
    
class PyCTP_Trader(PyCTP_Trader_API):
    
    def OrderActionDelete(self, order):
        """ 撤销报单 """
        return super().OrderAction(PyCTP.THOST_FTDC_AF_Delete, order['FrontID'], order['SessionID'], order['OrderRef'], order['ExchangeID'], order['OrderSysID'])
        
        