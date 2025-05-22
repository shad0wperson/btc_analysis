from flask import Flask, jsonify, render_template
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from SMA.data_processor import get_processed_data, generate_echarts_options
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables to store data and last update time
echarts_options = {}
last_updated_time = None
data_update_in_progress = False # Basic flag to prevent concurrent updates

def update_chart_data():
    '''Fetches new data, processes it, and updates global chart options and timestamp.'''
    global echarts_options, last_updated_time, data_update_in_progress
    
    if data_update_in_progress:
        logger.info("Data update already in progress. Skipping.")
        return

    data_update_in_progress = True
    logger.info("Starting data update...")
    try:
        processed_df = get_processed_data()
        echarts_options = generate_echarts_options(processed_df)
        last_updated_time = datetime.datetime.now()
        logger.info(f"Data update successful. Last updated: {last_updated_time.isoformat()}")
    except Exception as e:
        logger.error(f"Error updating chart data: {e}", exc_info=True)
    finally:
        data_update_in_progress = False

@app.route('/')
def index():
    # We will create templates/index.html in a later step
    return render_template('index.html', last_updated=last_updated_time.isoformat() if last_updated_time else "Not yet updated")

@app.route('/data')
def get_data_json(): # Renamed to avoid conflict with any 'data' variable
    global echarts_options, last_updated_time
    if not echarts_options:
        # This case might happen if the first scheduled job hasn't finished yet
        # or if there was an error during the initial update.
        logger.warning("ECharts options not available yet.")
        return jsonify({
            "error": "Data not available yet. Please try again in a moment.",
            "echarts_options": {},
            "last_updated": last_updated_time.isoformat() if last_updated_time else None
        }), 503 # Service Unavailable

    return jsonify({
        "echarts_options": echarts_options,
        "last_updated": last_updated_time.isoformat() if last_updated_time else None
    })

@app.route('/update_data', methods=['POST'])
def trigger_manual_update_data():
    global data_update_in_progress
    logger.info("Manual data update triggered by user.")
    if data_update_in_progress:
        return jsonify({"message": "Data update already in progress. Please wait."}), 429 # Too Many Requests
    
    # Run update in a separate thread to avoid blocking the request, 
    # although APScheduler also runs in background.
    # For simplicity here, direct call, but for long tasks, threading/task queue is better.
    update_chart_data() 
    return jsonify({"message": "Data update process started.", "last_updated": last_updated_time.isoformat() if last_updated_time else "Updating..."})

# Initialize and start APScheduler
scheduler = BackgroundScheduler()
# Schedule job to run every 30 minutes
scheduler.add_job(func=update_chart_data, trigger="interval", minutes=30)
# Schedule job to run once at startup, after a small delay to allow app to initialize
scheduler.add_job(func=update_chart_data, trigger="date", run_date=datetime.datetime.now() + datetime.timedelta(seconds=5))
scheduler.start()

# Ensure scheduler shuts down cleanly when app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # The initial data update is now handled by the scheduler.
    # app.run(debug=True, port=5000)
    # When using APScheduler with Flask's debug mode, it's common to set use_reloader=False
    # because the reloader can cause the scheduler to run jobs twice or behave unexpectedly.
    app.run(debug=True, port=5000, use_reloader=False)
