from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import json
import numpy as np

def add_vwap_signals(data, do_arrows=True, slope_degree=45, volumeLength=50):
    data['haClose'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
    data['haOpen'] = (data['Open'].shift(1) + data['Close'].shift(1)) / 2
    data['haBullish'] = data['haClose'] > data['haOpen']
    
    data['slopeDif'] = np.where(data['haBullish'], 
                                data['Close'] - data['Close'].shift(2),
                                data['Close'].shift(2) - data['Close'])
    data['slope'] = np.round(np.arctan(data['slopeDif']) * 180 / np.pi, 0)
    data['isDegreeOk'] = data['slope'] > slope_degree
    
    data['ema5'] = data['Close'].ewm(span=5, adjust=False).mean()
    data['ema12'] = data['Close'].ewm(span=12, adjust=False).mean()

    data['avgVol'] = ta.sma(data['Volume'], volumeLength)
    data['high_volume'] = data['Volume'] > data['avgVol']

    data['isRedCandle'] = data['Open'] > data['Close'] 
    data['isGreenCandle'] = data['Close'] > data['Open'] 

    # Green 
    data['ripsterSignalXup'] = (data['ema5'] > data['ema12']) & (data['ema5'].shift(1) <= data['ema12'].shift(1))
    data['ripsterSignalXdn'] = (data['ema5'] < data['ema12']) & (data['ema5'].shift(1) >= data['ema12'].shift(1))

    # magenta 
    data['priceAboveEMA5'] = (data['ema5'] > data['ema12']) & (data['Low'] < data['ema12']) & (data['Low'].shift(1) >= data['ema12'].shift(1)) & data['isRedCandle']
    data['priceBelowEMA5'] = (data['ema5'] < data['ema12']) & (data['High'] > data['ema12']) & (data['High'].shift(1) <= data['ema12'].shift(1)) & data['isGreenCandle']

    # Signal 
    if do_arrows:
        data['signal_up'] = data['high_volume'] & data['priceBelowEMA5'] 
        data['signal_down'] = data['high_volume'] & data['priceAboveEMA5'] 
        data['ripster_signal_up'] = data['ripsterSignalXup']
        data['ripster_signal_down'] = data['ripsterSignalXdn']
    else:
        data['signal_up'] = False
        data['signal_down'] = False
        data['ripster_signal_up'] = False
        data['ripster_signal_down'] = False
    
    data['debug_high_volume'] = data['high_volume'] 
    data['debug_ema5_gt_ema12'] = data['ema5'] > data['ema12']
    data['debug_ema5_lt_ema12'] = data['ema5'] < data['ema12']
    data['debug_low_cross_ema12'] = (data['Low'] < data['ema12']) & (data['Low'].shift(1) >= data['ema12'].shift(1))
    data['debug_high_cross_ema12'] = (data['High'] > data['ema12']) & (data['High'].shift(1) <= data['ema12'].shift(1))

    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['upperVwapCrossYellow'] = 0
    data['lowerVwapCrossYellow'] = 0
    data['upperVwapCrossGreen'] = 0
    data['lowerVwapCrossGreen'] = 0
    global resetUpper, resetLower,upperVwapCrossYellow, upperBand_vwap_cross_green, lowerBand_vwap_cross_green
    resetUpper = 1
    resetLower = 1
    upperVwapCrossYellow = 0
    lowerVwapCrossYellow = 0
    for i in range(0, len(data)):
        if data['RSI'].iloc[i] > 70:
            upperVwapCrossYellow = 1
        elif (upperVwapCrossYellow == 1) and resetUpper == 1 :
            upperVwapCrossYellow = 1
        else:
            upperVwapCrossYellow = 0

        upperBand_vwap_cross_green = upperVwapCrossYellow == 1 and data['Close'].iloc[i] < data['Open'].iloc[i] and data['MACDh_12_26_9'].iloc[i] < data['MACDh_12_26_9'].iloc[i-1]
        if(upperBand_vwap_cross_green):
            data.loc[data.index[i], 'upperVwapCrossGreen'] = 1
        else:
            data.loc[data.index[i], 'upperVwapCrossGreen'] = 0

        if data['upperVwapCrossGreen'].iloc[i] == 1:
            resetUpper = 0
        else:
            resetUpper = 1

        if data['RSI'].iloc[i] < 30:
            lowerVwapCrossYellow = 1
        elif (lowerVwapCrossYellow == 1) and resetLower == 1 :
            lowerVwapCrossYellow = 1
        else:
            lowerVwapCrossYellow = 0
        
        lowerBand_vwap_cross_green = lowerVwapCrossYellow == 1 and data['Close'].iloc[i] > data['Open'].iloc[i] and data['MACDh_12_26_9'].iloc[i] > data['MACDh_12_26_9'].iloc[i-1]
        if(lowerBand_vwap_cross_green):
            data.loc[data.index[i], 'lowerVwapCrossGreen'] = 1
        else:
            data.loc[data.index[i], 'lowerVwapCrossGreen'] = 0

        if data['lowerVwapCrossGreen'].iloc[i] == 1:
            resetLower = 0
        else:
            resetLower = 1



    # data['upperBand_vwap_cross_green'] = (data['upperVwapCrossYellow'] == 1) & (data['Close'] < data['Open']) & (data['MACDh_12_26_9'] < data['MACDh_12_26_9'].shift(1))
    # data['lowerBand_vwap_cross_green'] = (data['lowerVwapCrossYellow'] == 1) & (data['MACDh_12_26_9'] > data['MACDh_12_26_9'].shift(1)) & (data['Close'] > data['Open'])

    # data['upperVwapCrossGreen'] = data['upperBand_vwap_cross_green'].astype(int)
    # data['lowerVwapCrossGreen'] = data['lowerBand_vwap_cross_green'].astype(int)

    # for i in range(0, len(data)):
    #     # if data['upperVwapCrossGreen'].iloc[i] == 1:
    #     #     data.loc[data.index[i], 'resetUpper'] = 0
    #     # else:
    #     #     data.loc[data.index[i], 'resetUpper'] = 1

    #     if data['lowerVwapCrossGreen'].iloc[i] == 1:
    #         data.loc[data.index[i], 'resetLower'] = 0
    #     else:
    #         data.loc[data.index[i], 'resetLower'] = 1
    print(data.info())
    return data

def fetch_yahoo_data(ticker, interval, ema_period=20, macd_fast=12, macd_slow=26, macd_signal=9, vwap_period=20, vwap_std_dev=2):
    end_date = datetime.now()
    if interval in ['1m', '5m']:
        start_date = end_date - timedelta(days=7)       
    elif interval in ['15m', '60m']:
        start_date = end_date - timedelta(days=60)
    elif interval == '1d':
        start_date = end_date - timedelta(days=365*5)
    elif interval == '1wk':
        start_date = end_date - timedelta(weeks=365*5)
    elif interval == '1mo':
        start_date = end_date - timedelta(days=365*5)

    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    
    data['EMA'] = ta.ema(data['Close'], length=int(ema_period))

    macd = ta.macd(data['Close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    data = pd.concat([data, macd], axis=1)

    data = pd.DataFrame(data)
    data.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
    print(data.head())
    
    data['Volume_MA'] = data['Volume'].rolling(window=20).mean()

    data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])

    # Calculate VWAP bands
    data['VWAP_Std'] = data['VWAP'].rolling(window=vwap_period).std()
    data['VWAP_Upper'] = data['VWAP'] + (vwap_std_dev * data['VWAP_Std'])
    data['VWAP_Lower'] = data['VWAP'] - (vwap_std_dev * data['VWAP_Std'])
    data = add_vwap_signals(data)

    candlestick_data = [
        {
            'time': int(row.Index.timestamp()),
            'open': row.Open,
            'high': row.High,
            'low': row.Low,
            'close': row.Close
        }
        for row in data.itertuples()
    ]

    ema_data = [
        {
            'time': int(row.Index.timestamp()),
            'value': row.EMA
        }
        for row in data.itertuples() if not pd.isna(row.EMA)
    ]

    macd_data = [
        {
            'time': int(row.Index.timestamp()),
            'macd': row.MACD_12_26_9 if not pd.isna(row.MACD_12_26_9) else 0,
            'signal': row.MACDs_12_26_9 if not pd.isna(row.MACDs_12_26_9) else 0,
            'histogram': row.MACDh_12_26_9 if not pd.isna(row.MACDh_12_26_9) else 0
        }
        for row in data.itertuples()
    ]

    vwap_data = [
        {
            'time': int(row.Index.timestamp()),
            'vwap': row.VWAP if not pd.isna(row.VWAP) else 0,
            'upper': row.VWAP_Upper if not pd.isna(row.VWAP_Upper) else 0,
            'lower': row.VWAP_Lower if not pd.isna(row.VWAP_Lower) else 0
        }
        for row in data.itertuples()
    ]

    arrow_signals = [
        {
        'time': int(row.Index.timestamp()),
        'signal_up': bool(row.signal_up),
        'signal_down': bool(row.signal_down),
        'ripster_signal_up': bool(row.ripster_signal_up),
        'ripster_signal_down': bool(row.ripster_signal_down),
        'debug_high_volume': bool(row.Volume > row.avgVol),
        'debug_ema5_gt_ema12': bool(row.ema5 > row.ema12),
        'debug_low_cross_ema12': bool((row.Low < row.ema12) and (data['Low'].shift(1).iloc[i] >= data['ema12'].shift(1).iloc[i])),
        'isRedCandle': bool(row.isRedCandle),
        'debug_ema5_lt_ema12': bool(row.ema5 < row.ema12),
        'debug_high_cross_ema12': bool((row.High > row.ema12) and (data['High'].shift(1).iloc[i] <= data['ema12'].shift(1).iloc[i])),
        'isGreenCandle': bool(row.isGreenCandle),
        'ema5': row.ema5,
        'ema12': row.ema12,
        'low': row.Low,
        'high': row.High,
        'yellow_signal_up': bool(row.lowerVwapCrossGreen),
        'yellow_signal_down': bool(row.upperVwapCrossGreen)        
    }
    for i, row in enumerate(data.itertuples())
    ]
    
    return candlestick_data, ema_data, macd_data, vwap_data, arrow_signals