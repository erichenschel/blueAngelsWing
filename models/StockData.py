import finnhub
from datapackage import Package
import yfinance as yf

# scientific
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# utils
import requests
import json

class StockData():

    def __init__(self, stock):
        # stock name
        self.stock = stock

        # stock metrics
        self.request1 = requests.get('https://finnhub.io/api/v1/stock/metric?symbol=' + str(self.stock) + '&metric=all&token=bvt5fmf48v6rku8bvmn0').json()
        self.metrics = self.request1["metric"]

        # stock technical indicators
        self.request2 = requests.get('https://finnhub.io/api/v1/scan/technical-indicator?symbol=' + str(self.stock) + '&resolution=W&token=bvt5fmf48v6rku8bvmn0').json()
        try:
            self.techInd = self.request2["technicalAnalysis"]
            self.trends = self.request2["trend"]
        except:
            self.techInd = None
            self.trends = None

        # stock profile
        self.profile = requests.get('https://finnhub.io/api/v1/stock/profile2?symbol=' + str(self.stock) + '&token=bvt5fmf48v6rku8bvmn0').json()

        # stock quote
        self.quote = requests.get('https://finnhub.io/api/v1/quote?symbol=' + str(self.stock) + '&token=bvt5fmf48v6rku8bvmn0').json()

        # news sentiment
        self.sentiment = requests.get('https://finnhub.io/api/v1/news-sentiment?symbol=' + str(self.stock) + '&token=bvt5fmf48v6rku8bvmn0').json()["sentiment"]


    def getBeta(self):
        return self.metrics['beta']

    def getAvgVol(self):
        return self.metrics["10DayAverageTradingVolume"]

    def getBuySignal(self):
        return self.techInd["signal"]

    def getAdx(self):
        return self.trends["adx"]

    def getTrending(self):
        return self.trends["trending"]

    def getSharesOutstanding(self):
        return self.profile["shareOutstanding"]

    def getSpotPrice(self):
        return self.quote["c"]

    def getOpenPrice(self):
        return self.quote["o"]

    def getBullSentiment(self):
        return self.sentiment["bullishPercent"]

    def getBearSentiment(self):
        return self.sentiment["bearishPercent"]

    # returns a single row dataframe of data for a single stock
    def getStockData(self):
        data = {}
        data['symbol'] = [self.stock]
        data['spot'] = [self.getSpotPrice()]
        data['beta'] = [self.getBeta()]
        data['adx'] = [self.getAdx()]
        data['signal'] = [self.getBuySignal()]
        data['trending'] = [self.getTrending()]
        data['bearish'] = [self.getBearSentiment()]
        data['bullish'] = [self.getBullSentiment()]
        data['10_day_avg_vol'] = [self.getAvgVol()]
        data['shareOutstanding'] = [self.getSharesOutstanding()]

        data = pd.DataFrame.from_dict(data)
        return data