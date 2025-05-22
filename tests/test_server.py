import unittest
import sys
import os
import json
from datetime import datetime, timedelta 
import time

# Add project root to sys.path to allow importing server and SMA modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from server import app as flask_app 
    from SMA.data_processor import get_processed_data, generate_echarts_options
except ImportError as e:
    print(f"ImportError in test_server.py: {e}. Check sys.path and ensure all dependencies are available.")
    flask_app = None 

import pandas as pd

class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if flask_app is None:
            raise unittest.SkipTest("Skipping TestFlaskApp: Flask app could not be imported.")

        flask_app.testing = True
        cls.client = flask_app.test_client()
        
        print("TestFlaskApp.setUpClass: Ensuring initial data load by waiting for scheduler...")
        time.sleep(15) # Wait for server's initial data load (scheduled 5s + processing time)
        
        response = cls.client.get('/data')
        if response.status_code == 200:
            data = json.loads(response.data.decode('utf-8'))
            if not (data.get("echarts_options") and data.get("echarts_options").get("series")):
                print("WARNING: Initial data load for tests might have failed or is incomplete.")
        else:
             print(f"WARNING: /data endpoint returned {response.status_code} during test setup.")


    def test_01_index_page(self):
        if flask_app is None: self.skipTest("Flask app not imported.")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BTC Analysis Dashboard", response.data)

    def test_02_data_endpoint(self):
        if flask_app is None: self.skipTest("Flask app not imported.")
        response = self.client.get('/data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertIn("echarts_options", data)
        self.assertIn("last_updated", data)
        
        if not (data.get("echarts_options") and data.get("echarts_options").get("series")):
            self.skipTest("Skipping detailed /data checks as echarts_options are not populated.")

        self.assertIsInstance(data["echarts_options"], dict)
        self.assertIn("title", data["echarts_options"])
        self.assertIn("series", data["echarts_options"])
        self.assertTrue(len(data["echarts_options"]["series"]) > 0, "ECharts options should have series data.")

        if data["last_updated"]:
            try:
                datetime.fromisoformat(data["last_updated"])
            except ValueError:
                self.fail("last_updated is not a valid ISO format datetime string")

    def test_03_update_data_endpoint(self):
        if flask_app is None: self.skipTest("Flask app not imported.")
        
        initial_data_response = self.client.get('/data')
        self.assertEqual(initial_data_response.status_code, 200)
        initial_data = json.loads(initial_data_response.data.decode('utf-8'))
        initial_last_updated_str = initial_data.get("last_updated")
        
        update_response = self.client.post('/update_data')
        self.assertEqual(update_response.status_code, 200)
        update_data_json = json.loads(update_response.data.decode('utf-8'))
        self.assertIn("message", update_data_json)
        
        print("Waiting for /update_data to process in test_03_update_data_endpoint...")
        time.sleep(30) # Wait for data processing which involves external API calls

        final_data_response = self.client.get('/data')
        self.assertEqual(final_data_response.status_code, 200)
        final_data = json.loads(final_data_response.data.decode('utf-8'))
        final_last_updated_str = final_data.get("last_updated")

        self.assertIsNotNone(final_last_updated_str)
        
        if initial_last_updated_str and final_last_updated_str:
            initial_dt = datetime.fromisoformat(initial_last_updated_str)
            final_dt = datetime.fromisoformat(final_last_updated_str)
            self.assertTrue(final_dt > initial_dt - timedelta(seconds=10),
                            f"Expected new update time {final_last_updated_str} to be after/very close to {initial_last_updated_str}")
        
        self.assertTrue(final_data.get("echarts_options") and final_data.get("echarts_options").get("series"),
                        "ECharts options should be populated after manual update.")


class TestDataProcessor(unittest.TestCase):
    _shared_processed_df = None
    _data_fetch_error = False

    @classmethod
    def setUpClass(cls):
        print("TestDataProcessor.setUpClass: Fetching data for data processor tests...")
        try:
            cls._shared_processed_df = get_processed_data()
            if cls._shared_processed_df is None or cls._shared_processed_df.empty:
                print("WARNING: get_processed_data() returned None or empty DataFrame in TestDataProcessor.setUpClass.")
                cls._data_fetch_error = True
            else:
                print(f"Data fetched successfully for TestDataProcessor. Shape: {cls._shared_processed_df.shape}")
        except Exception as e:
            print(f"ERROR in TestDataProcessor.setUpClass during get_processed_data: {e}")
            cls._shared_processed_df = None # Ensure it's None on error
            cls._data_fetch_error = True


    def test_get_processed_data_returns_dataframe(self):
        if self._data_fetch_error or self._shared_processed_df is None:
            self.skipTest("Skipping due to data fetch error in TestDataProcessor.setUpClass.")
        
        self.assertIsInstance(self._shared_processed_df, pd.DataFrame)
        self.assertFalse(self._shared_processed_df.empty)
        
        expected_columns = ['Close', 'Low', 'High', 'SMA_200', 'Low_Percentage', 'High_Percentage', 'Fear_Greed']
        for col in expected_columns:
            self.assertIn(col, self._shared_processed_df.columns)
        
        self.assertFalse(self._shared_processed_df['Close'].isnull().all())


    def test_generate_echarts_options_returns_dict(self):
        if self._data_fetch_error or self._shared_processed_df is None or self._shared_processed_df.empty:
            self.skipTest("Skipping due to data fetch error or empty DataFrame in TestDataProcessor.setUpClass.")

        options = generate_echarts_options(self._shared_processed_df)
        self.assertIsInstance(options, dict)
        self.assertIn("title", options)
        self.assertIsInstance(options.get("title"), dict)
        self.assertIn("series", options)
        self.assertIsInstance(options.get("series"), list)
        self.assertTrue(len(options["series"]) >= 4) # BTC, SMA, Low_%, High_%
        self.assertIn("xAxis", options)
        self.assertIn("yAxis", options)

        if options["series"]:
            first_series = options["series"][0]
            self.assertIn("data", first_series)
            self.assertIsInstance(first_series.get("data"), list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
