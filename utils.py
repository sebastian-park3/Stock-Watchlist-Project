import json
import yfinance as yf
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta


stock_cache = {}


WATCHLIST = 'watchlist.json'


def save_watchlist(tickers):
    with open(WATCHLIST, 'w') as f:
        json.dump(tickers, f)

def load_watchlist():
    try:
        with open(WATCHLIST, 'r') as f:
            tickers = json.load(f)
        return tickers
    except FileNotFoundError as e:
        return []

def fetch_stock_data(ticker):
    current_time = datetime.now()
    if ticker in stock_cache:
        cached_data, cache_time = stock_cache[ticker]
        if current_time - cache_time < timedelta(minutes=15):
            return cached_data

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        if not data.empty:
            row = data.iloc[-1]
            price = row['Close']
            high = row['High']
            low = row['Low']
            volume = row['Volume']
            prev_close = stock.info.get('previousClose', price)
            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            date_time = row.name.strftime("%Y-%m-%d")

            return_data = {
                'ticker' : ticker,
                'price' : f'${price:.2f}',
                'date_time' : date_time,
                'change' : change,
                'change_pct' : change_pct,
                'high' : f'${high:.2f}',
                'low' : f'${low:.2f}',
                'volume' : f'{volume:,}'
            }

            stock_cache[ticker] = (return_data, current_time)
            return return_data
        else:
            return None
    except Exception:
        return None

