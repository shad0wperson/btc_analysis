from .data_fetcher import get_btc_data, get_fear_greed_index
from .indicator import calculate_percentages
import pandas as pd
import json # Not strictly needed here if we return dict, but good for consistency
import datetime

def get_processed_data():
    '''Fetches and processes BTC and Fear & Greed data.'''
    btc_df = get_btc_data()
    fear_greed_df = get_fear_greed_index()
    
    # Calculate percentages
    processed_df = calculate_percentages(btc_df.copy()) # Use .copy() to avoid SettingWithCopyWarning
    
    # Merge fear_greed_data (按索引对齐 - align by index)
    # Ensure index types are compatible for join. data_fetcher already converts to date.
    processed_df = processed_df.join(fear_greed_df, how='left')
    processed_df.rename(columns={
        'value': 'Fear_Greed',
        'value_classification': 'Fear_Greed_Class'
    }, inplace=True)
    
    return processed_df

def generate_echarts_options(data_df):
    '''Generates ECharts options dictionary from the processed DataFrame.'''
    # Ensure index is string date for JSON serialization if it becomes DatetimeIndex
    # data_fetcher.py already converts the index to date objects,
    # and get_processed_data returns it as such.
    # For ECharts, string dates are usually preferred.
    
    # Create a copy to safely modify for ECharts data preparation
    chart_df = data_df.copy()

    if isinstance(chart_df.index, pd.DatetimeIndex):
        chart_df["Date"] = chart_df.index.strftime("%Y-%m-%d")
    elif isinstance(chart_df.index, pd.Index) and pd.api.types.is_object_dtype(chart_df.index):
         # Assuming it's an index of date objects, convert to string
        chart_df["Date"] = chart_df.index.map(lambda x: x.strftime("%Y-%m-%d") if hasattr(x, 'strftime') else str(x))
    else: # Fallback for other index types
        chart_df["Date"] = chart_df.index.astype(str)

    # Data preparation for ECharts
    # 生成原始日期
    dates = chart_df["Date"].tolist()
    # 补充未来日期
    last_date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d")
    future_days = 1460  # 例如补充一年
    for i in range(1, future_days+1):
        future = last_date + datetime.timedelta(days=i)
        dates.append(future.strftime("%Y-%m-%d"))
    # 处理NaN值
    def replace_nan(val):
        return val if pd.notna(val) else None
    
    # 修改数据准备部分
    close = [replace_nan(x) for x in chart_df["Close"].round(2).tolist()]
    sma200 = [replace_nan(x) for x in chart_df["SMA_200"].round(2).tolist()]
    low_pct = [replace_nan(x) for x in chart_df["Low_Percentage"].round(2).tolist()]
    high_pct = [replace_nan(x) for x in chart_df["High_Percentage"].round(2).tolist()]
    fear_greed = [replace_nan(x) for x in chart_df["Fear_Greed"].tolist()]

    # Important events (Halving dates)
    halving_dates = ["2020-05-11", "2024-04-20", "2028-03-30"] # Keep as strings
    annotations = ["3. Halving", "4. Halving", "5. Halving"]

    # ECharts configuration (adapted from visualizer_echarts.py)
    option = {
        "title": {"text": "BTC Price and SMA Percentage Analysis"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["BTC价格", "SMA200", "相对SMA下降", "相对SMA上涨", "恐慌指数"], "top": "5%"}, # Adjust legend position
        "xAxis": {"type": "category", "data": dates, "axisPointer": {"show": True}},
        "yAxis": [
            {"type": "value", "name": "BTC Price (USD)"},
            {
                "type": "value",
                "name": "百分比(%)",
                "min": -70,
                "max": 200,
                "axisLabel": {"formatter": "{value}%"}
            },
            {"type": "value", "name": "恐慌指数", "min": 0, "max": 100, "position": "right", "offset": 80} # Increased offset
        ],
        "series": [
            {"name": "BTC价格", "type": "line", "data": close, "yAxisIndex": 0, "smooth": True, "lineStyle": {"color": "#FFA500", "width": 2}},
            {"name": "SMA200", "type": "line", "data": sma200, "yAxisIndex": 0, "smooth": True, "lineStyle": {"color": "#000080", "width": 2}},
            {
                "name": "相对SMA下降", 
                "type": "bar", 
                "data": low_pct, 
                "yAxisIndex": 1, 
                "itemStyle": {"color": "#FF0000", "opacity": 0.7},
                "markLine": {
                    "symbol": "none",
                    "data": [{"yAxis": -50, "label": {"formatter": "-50%"}}],
                    "lineStyle": {"type": "dashed", "color": "#FF0000", "width": 2}
                }
            },
            {"name": "相对SMA上涨", "type": "bar", "data": high_pct, "yAxisIndex": 1, "itemStyle": {"color": "#00CC00", "opacity": 0.7}},
            {"name": "恐慌指数", "type": "line", "data": fear_greed, "yAxisIndex": 2, "smooth": True, "lineStyle": {"color": "#FF69B4", "width": 1}}
        ],
        "dataZoom": [{"type": "slider", "start": 0, "end": 100, "bottom": "2%"}], # Adjust position
        "grid": {"right": "10%", "left": "8%", "bottom": "15%", "top": "15%"}, # Adjust grid
        "responsive": True # Added for better responsiveness if ECharts supports it directly
    }
    
    # Add halving events markLines to the series instead of top-level markLine for clarity
    # This is a common way to add vertical lines tied to specific dates
    # However, ECharts prefers markLines on specific series or globally if they are more general.
    # For vertical lines on xAxis, it's often clearer to add them to a relevant series or use global markLine.
    # The original code had a slightly unusual way of adding global markLine for halving dates.
    # Let's try to attach it to the first series (BTC Price) for better context or use a global approach.
    
    # Global markLine for halving dates:
    mark_line_data = []
    for d, a in zip(halving_dates, annotations):
        if d in dates: # Ensure the date exists in the current xAxis data
             mark_line_data.append({"xAxis": d, "label": {"formatter": a, "position": "insideEndTop"}})
        else:
            # Handle cases where halving date might be out of current data range (e.g. future dates)
            # Optionally, still add it if you want to denote future events, ECharts might just not show it if date is not on axis
            mark_line_data.append({"xAxis": d, "label": {"formatter": a, "position": "insideEndTop"}})


    if mark_line_data: # Only add if there are valid marklines
        option["series"][0]["markLine"] = { # Attaching to the first series (BTC Price)
             "symbol": ["none", "none"],
             "data": mark_line_data,
             "lineStyle": {"color": "#A9A9A9", "type": "dashed"}
        }
        
    return option

# Example usage (optional, for testing this module directly)
if __name__ == '__main__':
    print("Fetching and processing data...")
    df = get_processed_data()
    print("Data processed:")
    print(df.tail())
    
    print("\nGenerating ECharts options...")
    options = generate_echarts_options(df)
    # print(json.dumps(options, indent=4)) # Pretty print JSON
    print("ECharts options generated successfully. Keys:", options.keys())
