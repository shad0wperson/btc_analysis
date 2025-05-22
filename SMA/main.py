from data_fetcher import get_btc_data, get_fear_greed_index
from indicator import calculate_percentages
# from visualizer import plot_btc_analysis
from visualizer_echarts import plot_btc_analysis
def main():
    # 获取数据
    data = get_btc_data()
    # 获取恐慌指数数据
    fear_greed_data = get_fear_greed_index()
    # 计算百分比
    data = calculate_percentages(data)
    # 合并恐慌指数数据（按索引对齐）
    data = data.join(fear_greed_data, how='left')
    data.rename(columns={
        'value': 'Fear_Greed',
        'value_classification': 'Fear_Greed_Class'
    }, inplace=True)
    # 绘制图表
    plot_btc_analysis(data)

if __name__ == "__main__":
    main()