# smart_retail_engine/scripts/app_flask.py
from flask import Flask, jsonify, request
import os
import sys

# Add the project root directory to the Python path to allow imports from 'scripts'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import functions and variables from pipeline.py
from scripts.pipeline import load_models_and_data, get_recommendations_for_customer

app = Flask(__name__) # Initialize Flask app

# --- Model and Data Initialization (performed once when the app starts) ---
# These global variables will hold the loaded models and data
global_scaler = None
global_encoder = None
global_kmeans_latent = None
global_rfm_df = None
global_df_orders_clustered = None
global_cluster_top_items_dict = None
global_overall_top_products = None
global_rfm_features = None

try:
    global_scaler, global_encoder, global_kmeans_latent, \
    global_rfm_df, global_df_orders_clustered, \
    global_cluster_top_items_dict, global_overall_top_products, global_rfm_features = load_models_and_data()
    print("[INFO] All models and pre-calculated data loaded successfully for Flask app.")
except Exception as e:
    print(f"[ERROR] Flask app failed to load models or data: {e}")
    sys.exit(1) # Exit if models/data can't be loaded, as the app won't function

# --- Recommendation API Endpoint ---
@app.route('/recommendations/<customer_id>', methods=['GET'])
def api_get_recommendations(customer_id):
    """API endpoint to get recommendations for a given customer ID."""
    # Call the recommendation function from pipeline.py with loaded global assets
    result = get_recommendations_for_customer(
        customer_id,
        global_rfm_df,
        global_df_orders_clustered,
        global_scaler,
        global_encoder,
        global_kmeans_latent,
        global_cluster_top_items_dict,
        global_overall_top_products,
        global_rfm_features
    )
    
    # Return the dictionary as a JSON response
    return jsonify(result), 200

# --- Running the Flask Application ---
if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible from other machines in the network
    # For production, set debug=False and use a production-ready WSGI server (e.g., Gunicorn)
    app.run(debug=True, host='0.0.0.0', port=5000)