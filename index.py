import yfinance as yf
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime

app = Flask(__name__)

# List of sector-wise stock symbols from NSE
symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS",  # Add more symbols as needed
]

def get_sector_data():
    try:
        # Fetch stock data for the given symbols
        data = yf.download(symbols, period="1d", interval="1m")

        # Print available columns for debugging
        print("Available columns:", data.columns)

        # Check if 'Adj Close' exists; fallback to 'Close' if missing
        stock_data = data.get('Adj Close', data.get('Close'))
        
        # Handle case if no valid data is found
        if stock_data is None or stock_data.empty:
            return {"error": "No valid stock data available."}

        # Convert the index (timestamp) to string to avoid serialization issues
        stock_data.index = stock_data.index.astype(str)

        # Convert data to dictionary format for easier processing
        return stock_data.to_dict()

    except Exception as e:
        return {"error": str(e)}

# Define the background task function
def update_sector_data():
    current_time = datetime.now().time()
    start_time = datetime.strptime("10:00:00", "%H:%M:%S").time()
    end_time = datetime.strptime("15:30:00", "%H:%M:%S").time()

    # Only run the task if the current time is between 10:00 AM and 3:30 PM
    if start_time <= current_time <= end_time:
        print("Running background task to update sector data...")
        sector_data = get_sector_data()
        print("Sector data updated:", sector_data)
    else:
        print(f"Current time ({current_time}) is outside the market hours (10:00 AM - 3:30 PM). Task skipped.")

@app.route('/sector-heatmap')
def sector_heatmap():
    sector_data = get_sector_data()
    
    if "error" in sector_data:
        return jsonify({"status": "error", "message": sector_data["error"]}), 400
    
    return jsonify({"status": "success", "data": sector_data})

if __name__ == '__main__':
    # Set up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_sector_data, trigger="interval", seconds=50)  # Run every 50 seconds
    scheduler.start()

    # Ensure Flask is properly shut down with the scheduler
    try:
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
