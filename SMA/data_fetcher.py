import requests
import time
import pandas as pd
from datetime import datetime

def get_btc_data():
    url = "https://api.binance.com/api/v3/klines"
    symbol = "BTCUSDT"
    interval = "1d"
    start_time = int(datetime.strptime("2015-01-01", "%Y-%m-%d").timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    limit = 1000

    data = []
    current_time = start_time

    while current_time < end_time:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_time,
            "endTime": end_time,
            "limit": limit
        }
        response = requests.get(url, params=params)
        result = response.json()
        
        if not result:
            break
        
        for item in result:
            data.append({
                'Date': datetime.fromtimestamp(item[0] / 1000),
                'Low': float(item[3]),
                'High': float(item[2]),
                'Close': float(item[4])
            })
        
        current_time = result[-1][0] + 24 * 60 * 60 * 1000
        time.sleep(0.1)

    df = pd.DataFrame(data)
    df['Date'] = df['Date'].dt.date  # 新增：转换为 date 类型
    df.set_index('Date', inplace=True)
    return df

def get_fear_greed_index():
    # API 请求参数
    params = {
        "limit": 0,          # 获取全部数据
        "date_format": "world"  # 日期格式
    }

    # 发送 GET 请求
    url = "https://api.alternative.me/fng/"
    response = requests.get(url, params=params)
    data = response.json()

    # 转换为 DataFrame
    df = pd.DataFrame(data["data"])
    df["date"] = pd.to_datetime(df["timestamp"], format='%d-%m-%Y').dt.date
    
    # 创建新的DataFrame而不是修改切片
    result = pd.DataFrame()
    result['date'] = df['date']
    result['value'] = pd.to_numeric(df['value'])
    result['value_classification'] = df['value_classification']
    result.set_index('date', inplace=True)
    
    return result