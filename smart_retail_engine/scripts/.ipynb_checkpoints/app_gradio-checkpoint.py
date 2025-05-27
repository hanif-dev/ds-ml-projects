# smart_retail_engine/scripts/app_gradio.py
import gradio as gr
import requests
import os
import sys

# Add the project root directory to the Python path to allow imports from 'scripts'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Flask API URL Configuration ---
# Replace with your Flask server's IP/Domain if the API is running elsewhere
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")

def get_recommendations_gradio(customer_id):
    """Function to fetch recommendations from the Flask API for Gradio."""
    if not customer_id:
        return (
            "Please enter a Customer ID.", # status
            "N/A", "N/A", "N/A", "N/A", # Cluster, Source, RFM Details
            "N/A", # Purchased Products
            "No Customer ID provided.", # Personalized Recs
            "No Customer ID provided." # Overall Popular Recs
        )

    try:
        response = requests.get(f"{FLASK_API_URL}/recommendations/{customer_id}")
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if "error" in data:
            error_msg = f"Error: {data['error']}"
            return (
                error_msg,
                "N/A", "N/A", "N/A", "N/A", "N/A",
                "Error fetching recommendations.",
                "Error fetching recommendations."
            )
        else:
            # Prepare RFM details
            rfm_details = (
                f"**Recency Score:** {data.get('r_score', 'N/A')}<br>"
                f"**Frequency Score:** {data.get('f_score', 'N/A')}<br>"
                f"**Monetary Score:** {data.get('m_score', 'N/A')}<br>"
                f"**RFM Segment:** **{data.get('rfm_segment_label', 'N/A')}**"
            )

            # Prepare purchased products
            purchased_prods_text = "No purchase history found for this customer, or customer ID is new/invalid."
            if data.get('purchased_products'):
                purchased_prods_text = "\n".join([f"- {item}" for item in data['purchased_products']])

            # Prepare personalized recommendations
            personalized_recs_text = "No specific personalized recommendations found for this cluster, or all relevant items have been purchased."
            if data.get('cluster_based_recommendations'):
                personalized_recs_text = "\n".join([f"**{i+1}.** {item}" for i, item in enumerate(data['cluster_based_recommendations'])])

            # Prepare overall popular recommendations
            overall_popular_recs_text = "No overall popular recommendations available."
            if data.get('overall_popular_recommendations'):
                overall_popular_recs_text = "\n".join([f"**{i+1}.** {item}" for i, item in enumerate(data['overall_popular_recommendations'])])

            return (
                f"Recommendations found for: **{data['customer_id']}**",
                f"Autoencoder Cluster: **{data['cluster']}**",
                f"Recommendation Strategy: *{data['recommendation_source']}*",
                rfm_details,
                purchased_prods_text,
                personalized_recs_text,
                overall_popular_recs_text
            )
    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Flask API. Please ensure the API is running.",
            f"API URL: `{FLASK_API_URL}`", "N/A", "N/A", "N/A",
            "Connection error.",
            "Connection error."
        )
    except requests.exceptions.RequestException as e:
        return (
            f"Request error occurred: {e}",
            "N/A", "N/A", "N/A", "N/A", "N/A",
            "Request error.",
            "Request error."
        )
    except Exception as e:
        return (
            f"An unexpected error occurred: {e}",
            "N/A", "N/A", "N/A", "N/A", "N/A",
            "Unexpected error.",
            "Unexpected error."
        )

# Create the Gradio interface using gr.Blocks for more control
with gr.Blocks(title="Smart Retail Recommendation Engine (Gradio)") as demo:
    gr.Markdown("# 🛍️ Smart Retail Recommendation Engine")
    gr.Markdown("Get personalized product recommendations based on customer behavior and general popularity.")
    gr.Markdown("---")

    with gr.Row():
        customer_id_input = gr.Textbox(label="Enter Customer ID:", placeholder="Example: MW-18235", scale=2)
        submit_button = gr.Button("Get Recommendations", variant="primary", scale=1)
    
    gr.Markdown("---")
    
    # Output components
    status_output = gr.Markdown(label="Status")
    with gr.Row():
        cluster_output = gr.Markdown(label="Autoencoder Cluster")
        source_output = gr.Markdown(label="Recommendation Strategy")
    rfm_details_output = gr.Markdown(label="Customer RFM Information")
    
    gr.Markdown("---")
    gr.Markdown("### 🛒 Products You've Purchased Before")
    purchased_products_output = gr.Markdown(label="Purchased Products")
    
    gr.Markdown("---")
    gr.Markdown("### 🎯 Personalized Recommendations (Based on Your Cluster)")
    personalized_recs_output = gr.Markdown(label="Personalized Recommendations")
    
    gr.Markdown("---")
    gr.Markdown("### ✨ Overall Popular Products")
    overall_popular_recs_output = gr.Markdown(label="Overall Popular Products")

    # Connect the button to the function
    submit_button.click(
        fn=get_recommendations_gradio,
        inputs=customer_id_input,
        outputs=[
            status_output,
            cluster_output,
            source_output,
            rfm_details_output,
            purchased_products_output,
            personalized_recs_output,
            overall_popular_recs_output
        ]
    )
    
    gr.Markdown("---")
    gr.Info("This system uses Autoencoder-based customer segmentation, RFM analysis, and general popularity to provide relevant recommendations.")

if __name__ == "__main__":
    # Ensure Flask API is running separately at http://localhost:5000
    demo.launch()