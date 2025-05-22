import pandas as pd
import json

def plot_btc_analysis(data, output_html="/Users/martin/Documents/sma200/SMA/output/btc_analysis_echarts.html"):
    # 保证index为字符串日期
    data = data.copy()
    if isinstance(data.index, pd.DatetimeIndex):
        data["Date"] = data.index.strftime("%Y-%m-%d")
    else:
        data["Date"] = data.index.astype(str)

    # 数据准备
    dates = data["Date"].tolist()
    close = data["Close"].tolist()
    sma200 = data["SMA_200"].tolist()
    low_pct = data["Low_Percentage"].tolist()
    high_pct = data["High_Percentage"].tolist()
    fear_greed = data["Fear_Greed"].tolist()
    # 重要事件
    halving_dates = ["2020-05-11", "2024-04-20", "2028-03-30"]
    annotations = ["3. Halving", "4. Halving", "5. Halving"]

    # ECharts配置
    option = {
        "title": {"text": "BTC Price and SMA Percentage Analysis"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["BTC价格", "SMA200", "相对SMA下降", "相对SMA上涨", "恐慌指数"]},
        "xAxis": {"type": "category", "data": dates},
        "yAxis": [
            {"type": "value", "name": "BTC Price (USD)"},
            {
                "type": "value",
                "name": "百分比(%)",
                "min": -70,  # 最小值改为-70
                "max": 200,
                "axisLabel": {
                    "formatter": "{value}%"
                }
            },
            {"type": "value", "name": "恐慌指数", "min": 0, "max": 100, "position": "right", "offset": 60}
        ],
        "series": [
            {"name": "BTC价格", "type": "line", "data": close, "yAxisIndex": 0, "smooth": True, "lineStyle": {"color": "#FFA500", "width": 2}},
            {"name": "SMA200", "type": "line", "data": sma200, "yAxisIndex": 0, "smooth": True, "lineStyle": {"color": "#000080", "width": 2}},
            {"name": "相对SMA下降", "type": "bar", "data": low_pct, "yAxisIndex": 1, "itemStyle": {"color": "#FF0000", "opacity": 0.7},
             "markLine": {
                 "symbol": "none",
                 "data": [{"yAxis": -50, "label": {"formatter": ""}}],
                 "lineStyle": {"type": "dashed", "color": "#FF0000", "width": 3}
             }},
            {"name": "相对SMA上涨", "type": "bar", "data": high_pct, "yAxisIndex": 1, "itemStyle": {"color": "#00CC00", "opacity": 0.7}},
            {"name": "恐慌指数", "type": "line", "data": fear_greed, "yAxisIndex": 2, "smooth": True, "lineStyle": {"color": "#FF69B4", "width": 1}}
        ],
        "dataZoom": [{"type": "slider", "start": 0, "end": 100}],
        "grid": {"right": 120}
    }
    # 添加减半事件的标线
    option["xAxis"]["axisPointer"] = {"show": True}
    option["markLine"] = {
        "symbol": ["none", "none"],
        "data": [
            {"xAxis": d, "label": {"formatter": a}} for d, a in zip(halving_dates, annotations)
        ],
        "markLine": {
            "symbol": "none",
            "data": [{"yAxis": -50}],
            "lineStyle": {"type": "dashed", "color": "#A9A9A9"}
        }
    }
    # 生成HTML
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTC ECharts Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>html,body,#main{{height:100%;margin:0;padding:0;}}</style>
</head>
<body>
    <div id="main" style="width:100vw;height:90vh;"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {json.dumps(option, ensure_ascii=False)};
        myChart.setOption(option);
    </script>
</body>
</html>
'''
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"ECharts HTML已保存到: {output_html}")