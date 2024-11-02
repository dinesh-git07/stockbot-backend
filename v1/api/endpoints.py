from fastapi import APIRouter
from v1.api.services import fetch_yahoo_data
import pandas as pd
from fastapi import HTTPException
import yfinance as yf
from requests import request
from datetime import datetime, timedelta


router = APIRouter()

@router.get('/api/data/{ticker}/{interval}/{ema_period}/{vwap_period}/{vwap_std_dev}')
def get_data(ticker: str, interval: str, ema_period: int, vwap_period: int, vwap_std_dev: float):
    try:
        candlestick_data, ema_data, macd_data, vwap_data, vwap_signals = fetch_yahoo_data(
            ticker, interval, ema_period=ema_period, vwap_period=vwap_period, vwap_std_dev=vwap_std_dev
        )
        return {
            'candlestick': candlestick_data,
            'ema': ema_data,
            'macd': macd_data,
            'vwap': vwap_data,
            'vwap_signals': vwap_signals
        }
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get('/api/symbols')
def get_symbols():
    with open('symbols.txt') as f:
        symbols = [line.strip() for line in f]
    return symbols

