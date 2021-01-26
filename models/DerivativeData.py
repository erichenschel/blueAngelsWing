# packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import norm
from datetime import datetime
import time

import yfinance as yf

from StockData import StockData


class DerivativeData():

    def __init__(self):
        print("processing...")

    # data_path and file_name should be specified by user
    def getStockDataFrame(self):
        # get stock list
        data_path = "/Users/erichenschel/Documents/Projects/blueAngelsWing/data/"
        file_name = "all_stocks.csv"
        full_path = data_path + file_name
        stock_list = pd.read_csv(full_path).values.tolist()

        repeat = []
        df = pd.DataFrame()

        for s in stock_list:
            s = s[0]
            try:
                stock = StockData(s)
                if stock.getBeta() > 1.0:
                    df = df.append(stock.getStockData())
            except:
                # print(str(s) + ' data was not available')
                repeat.append(s)
                time.sleep(30)
                pass

        print("attempting: " + str(repeat))
        for s in repeat:
            try:
                stock = StockData(s)
                if float(stock.getBeta()) > 1.0:
                    df = df.append(stock.getStockData())
            except:
                print(str(s) + ' data was not available')
                time.sleep(30)
        
        return df

    # collect all trending stocks in a dataframe
    def getTrendingStocks(self):
        df = self.getStockDataFrame().sort_values(by=["trending"], axis=0, ascending=False)
        trending_df = pd.DataFrame()

        for index, row in df.iterrows():
            if(row["trending"]):
                trending_df = trending_df.append(row)

        print(trending_df)
        return trending_df

    def getExpirDates(self, stock):
        # get options dates
        dates = None

        try:
            s = yf.Ticker(str(stock))
            dates = list(s.options)
        except:
            print("couldn't find expir dates for " + str(stock) + "...")

        return dates

    # calculating amnt of time to expiration in years
    def getTimeToExpir(self, date):
        ex_date = date.replace('-', '')
        year = int(ex_date[:4])
        month = int(ex_date[4:6])
        day = int(ex_date[6:])

        then = datetime(year, month, day)        
        now = datetime.now()
        duration = then - now
        delta_expir = float(duration.total_seconds())/(365.24*24*60*60)

        return delta_expir

    def getCallChain(self, underly, date):
        # get options chain (call)
        s = yf.Ticker(str(underly))
        call_chain = s.option_chain(date)[0]
        return call_chain

    def getPutChain(self, underly, date):
        s = yf.Ticker(str(underly))
        put_chain = s.option_chain(date)[1]
        return put_chain


    def getDerivativeDataFrame(self):
        for index, row in self.getTrendingStocks().iterrows():
            # get spot price
            spot = StockData(index).getSpotPrice()

            op_interest = pd.DataFrame()
            bs_ls = []

            dates = self.getExpirDates(index)

            # get expiration dates for first two dates
            for date in dates[:2]:
                delta_expir = self.getTimeToExpir(date)
                call_chain = self.getCallChain(index, date)
        
                # iterate through call chain
                for index, row in call_chain.iterrows():
                    # get strike price & impliedVolatility
                    strike = row['strike']
                    vol = row["impliedVolatility"]

                    # use BlackScholes model
                    rate = float(1.1/100.0)
                    bs_price = self.BS(spot, strike, rate, vol, delta_expir, CallPutFlag = 'C')

                    # is the true value of the option less than (thresh) * (100) = $500 (in this case)?
                    thresh = 10.0
                    if abs(spot-strike) < thresh:
                        # is the volatility of the option greater than 67%?
                        if float(vol) > .67:
                            # is the cost going to be more than 1k?
                            if float(row['lastPrice']) < 10.0:
                                # add to option dataframe if conditions are met
                                op_interest = op_interest.append(row, ignore_index=True)
                                bs_ls.append(round(bs_price, 4))

        drop_list = ["ask", "bid", "contractSize", "currency", "inTheMoney", "lastTradeDate"]
        try:
            op_interest = op_interest.drop(drop_list, axis=1)
        except:
            pass
    
        if op_interest.empty:
            pass
    #         print("No options of interest for " + str(stock) + " today.")
        else:
            op_interest['bsPrice'] = bs_ls
            cols = ["contractSymbol", "lastPrice", "bsPrice", "strike", "change", "impliedVolatility", "percentChange", "volume", "openInterest"]
            op_interest = op_interest[cols]
            op_interest = op_interest.sort_values(by=["lastPrice"], axis=0, ascending=True)

        return op_interest


    # black scholes function
    def BS(self, spot, strike, rate, ImpVol, expir, CallPutFlag = 'C'):
        d1 = (np.log(spot / strike) + 
          ((rate + (ImpVol**2 / float(2))) * expir)) * (float(1) / (ImpVol* np.sqrt(expir)))

        d2 = d1 - ImpVol * np.sqrt(expir)

        if CallPutFlag == 'C':
            call = spot * norm.cdf(d1) - strike * np.exp(-rate * expir) * norm.cdf(d2)
            return float(call)
        elif CallPutFlag == 'P':
            put = norm.cdf(-d2) * strike * np.exp(-rate * expir) - norm.cdf(-d1) * spot
            return float(put)
    
        return print("Error must have occurred...")

if __name__ == "__main__":
    d = DerivativeData()
    print(d.getDerivativeDataFrame())