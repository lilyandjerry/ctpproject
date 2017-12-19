#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 21:48:07 2016

@author: Zhuolin
"""

if __name__ == '__main__':
    import time, os, datetime, PyCTP
    from os.path import join, split, dirname, exists
    from PyCTP_Trader import PyCTP_Trader
    os.makedirs('tmp', exist_ok=True)
    trader = PyCTP_Trader.CreateFtdcTraderApi( join(b'tmp', b'test_t_') )
    time.sleep(1.0)
    #print('连接前置服务器:', trader.Connect(b'tcp://180.168.146.187:10030'))
    print('连接前置服务器:', trader.Connect(b'tcp://180.168.146.187:10000'))
    time.sleep(1.0)
    print('登陆:', trader.Login(b'9999', bytes(input('enter username:'), 'gbk'), bytes(input('enter password:'), 'gbk')))
    time.sleep(1.0)
    print('设置投资者:', trader.setInvestorID(bytes(input('enter investor ID:'), 'gbk')))
    time.sleep(1.0)
    print('查询投资者:')
    Investor = trader.QryInvestor()
    print('经纪公司代码:', Investor['BrokerID'])
    print('投资者代码:', Investor['InvestorID'])
    print('投资者名称:', str(Investor['InvestorName'], 'gbk'))
    print('联系方式:', '电话', str(Investor['Telephone'],'gbk'), '手机', str(Investor['Mobile'], 'gbk'), '地址', str(Investor['Address'], 'gbk'))
    time.sleep(1.0)
    print('查询资金账户:')
    account = trader.QryTradingAccount()
    print('手续费:', account['Commission'])
    print('平仓盈亏:', account['CloseProfit'])
    print('持仓盈亏:', account['PositionProfit'])
    print('可用资金:', account['Available'])
    print('动态权益:', account['Balance'])
    time.sleep(1.0)
    print('查询投资者结算结果:\n', str(trader.QrySettlementInfo()['Content'], 'gbk'))
    time.sleep(1.0)
    print('投资者结算信息确认:', trader.QrySettlementInfoConfirm())
    time.sleep(1.0)
    print('查询交易所与合约:\n')
    exchanges = trader.QryExchange()
    for exchange in exchanges:
        # 交易所
        print(exchange['ExchangeID'], str(exchange['ExchangeName'], 'gbk'))
        time.sleep(1.0)
        # 合约
        Instruments = trader.QryInstrument(ExchangeID=exchange['ExchangeID'])
        for instrument in Instruments:
            time.sleep(1.0)
            # 手续费
            commissionrate = trader.QryInstrumentCommissionRate(instrument['InstrumentID'])[0]
            time.sleep(1.0)
            # 保证金
            marginrate = trader.QryInstrumentMarginRate(instrument['InstrumentID'])[0]
            time.sleep(1.0)
            # 深度行情
            DepthMarketData = trader.QryDepthMarketData(instrument['InstrumentID'])[0]
            
            #print(marginrate)
            
            LongMarginRatio = max(instrument['LongMarginRatio'], marginrate['LongMarginRatioByMoney'])
            ShortMarginRatio = max(instrument['ShortMarginRatio'], marginrate['ShortMarginRatioByMoney'])
            print(instrument['ExchangeID']
            , instrument['InstrumentID']
            , str(instrument['InstrumentName'], 'gbk')
            , '乘数', instrument['VolumeMultiple']
            , '变动', instrument['PriceTick']
            , '开仓手续费', (commissionrate['OpenRatioByMoney'], commissionrate['OpenRatioByVolume'])
            , '平仓手续费', (commissionrate['CloseRatioByMoney'], commissionrate['CloseRatioByVolume'])
            , '平今手续费', (commissionrate['CloseTodayRatioByMoney'], commissionrate['CloseTodayRatioByVolume'])
            , '保证金', ((LongMarginRatio, marginrate['LongMarginRatioByVolume']), (ShortMarginRatio, marginrate['ShortMarginRatioByVolume']))
            )
            uptime = None            
            if DepthMarketData['ActionDay'] != b'' and DepthMarketData['UpdateTime'] != b'':
                uptime=datetime.datetime.strptime(str(DepthMarketData['ActionDay']+DepthMarketData['UpdateTime'], 'gbk'), '%Y%m%d%H:%M:%S').replace(microsecond=DepthMarketData['UpdateMillisec']*1000)            
            a = DepthMarketData['LastPrice'] * instrument['VolumeMultiple'] * (commissionrate['OpenRatioByMoney'] + commissionrate['CloseTodayRatioByMoney']) + commissionrate['OpenRatioByVolume'] + commissionrate['CloseTodayRatioByVolume']
            b = instrument['PriceTick'] * instrument['VolumeMultiple']
            c = a/b
            print(uptime
            , '最新价', DepthMarketData['LastPrice']
            , '数量', DepthMarketData['Volume']
            , '成交金额', DepthMarketData['Turnover']
            , '持仓量', DepthMarketData['OpenInterest']
            , '卖价一', DepthMarketData['AskPrice1']
            , '买价一', DepthMarketData['BidPrice1']
            , '卖量一', DepthMarketData['AskVolume1']
            , '买量一', DepthMarketData['BidVolume1']
            , '成本', c
            )
            break
    time.sleep(1.0)
    print('投资者持仓', trader.QryInvestorPosition())
    time.sleep(1.0)
    print('投资者持仓明细', trader.QryInvestorPositionDetail())
    time.sleep(1.0)
    print('查询报单:')
    orders = trader.QryOrder()
    for order in orders:
        order['StatusMsg'] = str(order['StatusMsg'], 'gbk')
        #break
    print(orders)
    time.sleep(1.0)
    print('查询成交: \n')
    for Trade in trader.QryTrade():
        print(Trade['InstrumentID'], Trade['ExchangeID'], Trade['TradeID'])
        #break
    time.sleep(1.0)
    print('申报开仓:', trader.OrderInsert(b'pp1602', PyCTP.THOST_FTDC_OF_Open, PyCTP.THOST_FTDC_D_Buy, 0, 0.0))
    time.sleep(1.0)
    #print('撤消申报:', trader.OrderActionDelete(order))
    while input('enter q to quit this program:') is not 'q':
        pass
    time.sleep(1.0)
    print('登出:', trader.Logout())

