def calculate_percentages(data):
    # 计算200日SMA
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    
    # 计算最低价相对于SMA的下降百分比（显示为负值）
    data['Low_Percentage'] = -1 * (data['SMA_200'] - data['Low']) / data['SMA_200'] * 100
    data.loc[data['Low_Percentage'] > 0, 'Low_Percentage'] = 0  # 只保留负值
    
    # 计算最高价相对于SMA的上涨百分比（显示为正值）
    data['High_Percentage'] = (data['High'] - data['SMA_200']) / data['SMA_200'] * 100
    data.loc[data['High_Percentage'] < 0, 'High_Percentage'] = 0  # 只保留正值
    
    return data