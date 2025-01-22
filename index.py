import yfinance as yf
from flask import Flask, jsonify
import os

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

@app.route('/sector-heatmap')
def sector_heatmap():
    sector_data = get_sector_data()
    
    if "error" in sector_data:
        return jsonify({"status": "error", "message": sector_data["error"]}), 400
    
    return jsonify({"status": "success", "data": sector_data})

if __name__ == '__main__':
    # Get port dynamically from environment variables (Railway sets this automatically)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
