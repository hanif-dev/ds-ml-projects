# smart_retail_engine/scripts/app_streamlit.py
import streamlit as st
import requests
import os
import sys

# Add the project root directory to the Python path to allow imports from 'scripts'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Flask API URL Configuration ---
# Get Flask API URL from environment variable or default to localhost
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000") 

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Smart Retail Recommender", layout="centered")

# --- Streamlit UI Elements ---
st.title("🛍️ Smart Retail Recommendation Engine")
st.markdown("Get personalized product recommendations based on customer behavior and general popularity.")

# Text input for Customer ID
customer_id = st.text_input(
    "Enter Customer ID:",
    value="",
    placeholder="Example: MW-18235" # Example from your data
)

# Button to trigger recommendations
if st.button("Get Recommendations", type="primary"):
    if customer_id:
        with st.spinner("Fetching recommendations..."): # Show spinner while fetching
            try:
                # Make a GET request to the Flask API
                response = requests.get(f"{FLASK_API_URL}/recommendations/{customer_id}")
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                data = response.json() # Parse JSON response

                if "error" in data: # Check for custom error messages from Flask API
                    st.error(f"An error occurred: {data['error']}")
                else:
                    st.success("Recommendations found!")
                    st.subheader(f"For Customer: {data['customer_id']}")
                    st.write(f"Autoencoder Cluster: **{data['cluster']}**")
                    st.write(f"Recommendation Strategy: *{data['recommendation_source']}*")

                    st.markdown("---") # Separator for visual clarity

                    # --- Display Customer RFM Information ---
                    st.markdown("### 📊 Customer RFM Information")
                    st.write(f"**Recency Score:** {data.get('r_score', 'N/A')}")
                    st.write(f"**Frequency Score:** {data.get('f_score', 'N/A')}")
                    st.write(f"**Monetary Score:** {data.get('m_score', 'N/A')}")
                    st.write(f"**RFM Segment:** **{data.get('rfm_segment_label', 'N/A')}**")

                    st.markdown("---") # Separator

                    # --- Display Products Purchased Before (Excerpt from User-Item Matrix) ---
                    st.markdown("### 🛒 Products You've Purchased Before")
                    if data.get('purchased_products'):
                        # Display as a bulleted list for clarity
                        for i, item in enumerate(data['purchased_products']):
                            st.write(f"- {item}")
                    else:
                        st.info("No purchase history found for this customer, or customer ID is new/invalid.")

                    st.markdown("---") # Separator

                    # --- Display Personalized (Cluster-Based) Recommendations ---
                    st.markdown("### 🎯 Personalized Recommendations (Based on Your Cluster)")
                    st.markdown("These products are recommended based on the purchasing patterns of customers similar to you.")
                    if data['cluster_based_recommendations']:
                        for i, item in enumerate(data['cluster_based_recommendations']):
                            st.write(f"**{i+1}.** {item}")
                    else:
                        st.info("No specific personalized recommendations found for this cluster, or all relevant items have been purchased.")

                    st.markdown("---") # Separator

                    # --- Display Overall Popular Recommendations ---
                    st.markdown("### ✨ Overall Popular Products")
                    st.markdown("These are popular items across all customers, useful as general suggestions.")
                    if data['overall_popular_recommendations']:
                        for i, item in enumerate(data['overall_popular_recommendations']):
                            st.write(f"**{i+1}.** {item}")
                    else:
                        st.warning("No overall popular recommendations available.")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Flask API. Please ensure the API is running at "
                         f"`{FLASK_API_URL}`.")
            except requests.exceptions.RequestException as e:
                st.error(f"A request error occurred: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a Customer ID to get recommendations.")

st.markdown("---")
st.info("This system uses Autoencoder-based customer segmentation, RFM analysis, and general popularity to provide relevant recommendations.")