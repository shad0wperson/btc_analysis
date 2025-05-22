import json
import os
# Import the new centralized function
from .data_processor import generate_echarts_options, get_processed_data

# Default output path for the standalone HTML file (consider making this relative)
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DEFAULT_OUTPUT_HTML_FILE = os.path.join(DEFAULT_OUTPUT_DIR, "btc_analysis_echarts_standalone.html")

def plot_btc_analysis_standalone(data_df, output_html=DEFAULT_OUTPUT_HTML_FILE):
    '''
    Generates ECharts options using the centralized function and saves a standalone HTML file.
    '''
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_html)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Generate ECharts options using the centralized function
    option = generate_echarts_options(data_df)

    # Generate HTML (similar to the original visualizer_echarts.py)
    # The ECharts option object is now sourced from generate_echarts_options
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BTC ECharts Visualization (Standalone)</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>html,body,#main{{height:100%;margin:0;padding:0;}}</style>
</head>
<body>
    <div id="main" style="width:100vw;height:90vh;"></div> {/* Consider making width/height more flexible */}
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {json.dumps(option, ensure_ascii=False, indent=None)}; // Use indent=None for compactness in HTML
        myChart.setOption(option);
        // Optional: Add resize listener if this HTML is viewed directly
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>
'''
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Standalone ECharts HTML saved to: {output_html}")

# Example usage (for testing this module directly)
if __name__ == "__main__":
    print("Fetching and processing data for standalone visualizer...")
    df = get_processed_data() # Use the centralized data fetching too
    print("Data processed. Now generating standalone HTML chart...")
    plot_btc_analysis_standalone(df)
    print(f"Standalone chart generated at {DEFAULT_OUTPUT_HTML_FILE}")