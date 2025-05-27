# smart_retail_engine/scripts/pipeline.py
import pandas as pd
import numpy as np
import os
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input, Dense
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from datetime import datetime

# --- Path Configurations (relative to the project root) ---
_current_script_dir = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_DIR = os.path.join(_current_script_dir, '..', 'data', 'processed')
MODELS_DIR = os.path.join(_current_script_dir, '..', 'models')
RAW_DATA_PATH = os.path.join(_current_script_dir, '..', 'data', 'raw', 'global-superstore.xlsx')


# --- Main Pipeline Functions ---

def load_and_preprocess_data(file_path=RAW_DATA_PATH):
    """Loads raw data and performs initial preprocessing."""
    df_orders = pd.read_excel(file_path, sheet_name="Orders")
    df_returns = pd.read_excel(file_path, sheet_name="Returns")

    if 'Postal Code' in df_orders.columns:
        df_orders = df_orders.drop(columns=['Postal Code'])

    df_orders = df_orders.merge(df_returns[["Order ID", "Returned"]], on="Order ID", how="left")
    df_orders["Returned"] = df_orders["Returned"].fillna("No").astype("category")

    df_orders["Shipping Duration"] = (df_orders["Ship Date"] - df_orders["Order Date"]).dt.days
    df_orders["Order Year"] = df_orders["Order Date"].dt.year
    df_orders["Order Month"] = df_orders["Order Date"].dt.month
    df_orders['Discount Rate'] = df_orders['Discount'] / (1 - df_orders['Discount'])
    df_orders['Sales Category'] = pd.cut(df_orders['Sales'], bins=[0, 100, 500, 1000, 100000], labels=['Low', 'Medium', 'High', 'Very High'])

    df_orders_ca = df_orders.copy()
    positive_profit_mask = df_orders_ca['Profit'] > 0
    df_orders_ca['Profit_log'] = df_orders_ca['Profit'].copy()
    df_orders_ca.loc[positive_profit_mask, 'Profit_log'] = np.log1p(df_orders_ca.loc[positive_profit_mask, 'Profit'])
    epsilon = np.finfo(float).eps
    df_orders_ca['Sales_log'] = np.log1p(df_orders_ca['Sales'].replace(0, epsilon))
    df_orders_ca['Quantity_log'] = np.log1p(df_orders_ca['Quantity'].replace(0, epsilon))

    return df_orders_ca


def calculate_rfm(df_orders_ca):
    """Calculates Recency, Frequency, Monetary metrics."""
    df_orders_ca['Order Date'] = pd.to_datetime(df_orders_ca['Order Date'])
    analysis_date = df_orders_ca['Order Date'].max() + pd.Timedelta(days=1)

    recency_df = df_orders_ca.groupby('Customer ID')['Order Date'].max().reset_index()
    recency_df['Recency'] = (analysis_date - recency_df['Order Date']).dt.days
    recency_df = recency_df[['Customer ID', 'Recency']]

    frequency_df = df_orders_ca.groupby('Customer ID')['Order ID'].nunique().reset_index()
    frequency_df.columns = ['Customer ID', 'Frequency']

    monetary_df = df_orders_ca.groupby('Customer ID')['Sales'].sum().reset_index()
    monetary_df.columns = ['Customer ID', 'Monetary']

    rfm_df = recency_df.merge(frequency_df, on='Customer ID')
    rfm_df = rfm_df.merge(monetary_df, on='Customer ID')
    return rfm_df

def score_rfm_and_cluster(rfm_df, n_clusters_optimal=3):
    """Scores RFM and performs Autoencoder clustering."""
    segment_count = 5
    rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=segment_count, labels=range(segment_count, 0, -1), duplicates='drop').astype(int)
    rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'], q=segment_count, labels=range(1, segment_count + 1), duplicates='drop').astype(int)
    rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=segment_count, labels=range(1, segment_count + 1), duplicates='drop').astype(int)
    
    # Map RFM Score to a more descriptive segment name
    def rfm_segment_label(row):
        # Example RFM segmentation logic (you can customize this)
        if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
            return 'Champions'
        elif row['R_Score'] >= 4 and row['F_Score'] >= 3:
            return 'Loyal Customers'
        elif row['R_Score'] >= 3 and row['M_Score'] >= 3:
            return 'Potential Loyalists'
        elif row['R_Score'] <= 2 and row['M_Score'] >= 3:
            return 'Big Spenders'
        elif row['R_Score'] <= 2 and row['F_Score'] <= 2:
            return 'At Risk'
        elif row['R_Score'] >= 3 and row['F_Score'] <= 2:
            return 'Needs Attention'
        else:
            return 'Other' # For any unhandled combinations

    rfm_df['RFM_Segment_Label'] = rfm_df.apply(rfm_segment_label, axis=1)
    
    rfm_df['RFM_Segment'] = rfm_df['R_Score'].astype(str) + rfm_df['F_Score'].astype(str) + rfm_df['M_Score'].astype(str)
    rfm_df['RFM_Score'] = rfm_df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    rfm_features = ['Recency', 'Frequency', 'Monetary']
    X = rfm_df[rfm_features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    input_dim = X_scaled.shape[1]
    latent_dim = 2
    
    input_layer = Input(shape=(input_dim,))
    encoder_layer = Dense(8, activation='relu')(input_layer)
    encoder_layer = Dense(4, activation='relu')(encoder_layer)
    latent_space = Dense(latent_dim, activation='relu', name='latent_space')(encoder_layer)
    decoder_layer = Dense(4, activation='relu')(latent_space)
    decoder_layer = Dense(8, activation='relu')(decoder_layer)
    output_layer = Dense(input_dim, activation='linear')(decoder_layer)
    autoencoder = Model(inputs=input_layer, outputs=output_layer)
    autoencoder.compile(optimizer='adam', loss='mse')
    autoencoder.fit(X_scaled, X_scaled, epochs=50, batch_size=32, shuffle=True, verbose=0)
    encoder = Model(inputs=input_layer, outputs=latent_space)

    X_latent = encoder.predict(X_scaled)

    kmeans_latent = KMeans(n_clusters=n_clusters_optimal, random_state=42, n_init=10)
    rfm_df['Cluster_AE'] = kmeans_latent.fit_predict(X_latent)

    return rfm_df, scaler, encoder, kmeans_latent, rfm_features


def save_models_and_data(rfm_df, df_orders_ca_with_clusters, scaler, encoder, kmeans_latent):
    """Saves processed data and trained models."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    rfm_df.to_csv(os.path.join(PROCESSED_DATA_DIR, "rfm_df.csv"), index=False)
    df_orders_ca_with_clusters.to_csv(os.path.join(PROCESSED_DATA_DIR, "df_orders_ca_with_clusters.csv"), index=False)
    
    joblib.dump(scaler, os.path.join(MODELS_DIR, "rfm_scaler.joblib"))
    joblib.dump(kmeans_latent, os.path.join(MODELS_DIR, "kmeans_latent_model.joblib"))
    encoder.save(os.path.join(MODELS_DIR, "autoencoder_encoder_model.h5"))
    print("[INFO] Models and processed data saved.")


def load_models_and_data():
    """Loads saved models and pre-calculated data for real-time inference."""
    # Added compile=False for safety when loading H5 models in newer TF versions
    scaler = joblib.load(os.path.join(MODELS_DIR, "rfm_scaler.joblib"))
    encoder = load_model(os.path.join(MODELS_DIR, "autoencoder_encoder_model.h5"), compile=False) 
    kmeans_latent = joblib.load(os.path.join(MODELS_DIR, "kmeans_latent_model.joblib"))
    
    rfm_df_global = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "rfm_df.csv"))
    df_orders_clustered_global = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "df_orders_ca_with_clusters.csv"))

    cluster_top_items_dict = {}
    for cluster_id in sorted(df_orders_clustered_global['Cluster_AE'].unique()):
        cluster_data = df_orders_clustered_global[df_orders_clustered_global['Cluster_AE'] == cluster_id]
        # Get top 20 items from each cluster to give more options after filtering
        top_items = cluster_data['Product Name'].value_counts().index.tolist()[:20] 
        cluster_top_items_dict[cluster_id] = top_items
    
    # Get top 15 overall popular products
    overall_top_products_global = df_orders_clustered_global['Product Name'].value_counts().head(15).index.tolist()

    rfm_features = ['Recency', 'Frequency', 'Monetary']

    return scaler, encoder, kmeans_latent, rfm_df_global, df_orders_clustered_global, cluster_top_items_dict, overall_top_products_global, rfm_features


def get_recommendations_for_customer(customer_id, rfm_df_global, df_orders_clustered_global, scaler, encoder, kmeans_latent, cluster_top_items_dict, overall_top_products_global, rfm_features, top_n_cluster=5, top_n_overall=5):
    """
    Provides both cluster-based and overall popularity-based recommendations for a given customer ID,
    prioritizing unique cluster recommendations, and includes RFM details and purchased products.
    """
    # Use .copy() to prevent SettingWithCopyWarning later
    customer_rfm = rfm_df_global[rfm_df_global['Customer ID'] == customer_id].copy() 
    
    cluster_recommendations = []
    customer_cluster = "Unknown"
    recommendation_source = ""
    purchased_products_current_customer = []
    
    # Default RFM info if customer not found
    customer_r_score = "N/A"
    customer_f_score = "N/A"
    customer_m_score = "N/A"
    customer_rfm_segment_label = "N/A"

    if customer_rfm.empty:
        recommendation_source = "Popularity-based (Customer not found)"
        final_overall_popular_recs = overall_top_products_global[:top_n_overall]
    else:
        try:
            customer_rfm_scaled = scaler.transform(customer_rfm[rfm_features].values)
            customer_latent_feature = encoder.predict(customer_rfm_scaled, verbose=0)
            customer_cluster = int(kmeans_latent.predict(customer_latent_feature)[0])

            # Get RFM scores and segment label for the current customer
            customer_r_score = int(customer_rfm['R_Score'].iloc[0])
            customer_f_score = int(customer_rfm['F_Score'].iloc[0])
            customer_m_score = int(customer_rfm['M_Score'].iloc[0])
            customer_rfm_segment_label = customer_rfm['RFM_Segment_Label'].iloc[0]

            recommendations_pool = cluster_top_items_dict.get(customer_cluster, [])
            
            # Get products already purchased by the current customer
            purchased_products_current_customer = df_orders_clustered_global[
                df_orders_clustered_global['Customer ID'] == customer_id
            ]['Product Name'].unique().tolist()
            
            # Filter cluster recommendations: remove already purchased items
            filtered_recs_cluster = [rec for rec in recommendations_pool if rec not in purchased_products_current_customer]
            cluster_recommendations = filtered_recs_cluster[:top_n_cluster]
            
            if cluster_recommendations:
                recommendation_source = "Hybrid (Cluster-based with bought item filter)"
            else:
                recommendation_source = "Popularity-based (Cluster recommendations exhausted or none)"
            
            # Ensure overall popular recommendations do not duplicate cluster recommendations or purchased items
            cluster_recs_set = set(cluster_recommendations)
            purchased_recs_set = set(purchased_products_current_customer)
            
            filtered_overall_popular = [
                rec for rec in overall_top_products_global 
                if rec not in cluster_recs_set and rec not in purchased_recs_set
            ]
            final_overall_popular_recs = filtered_overall_popular[:top_n_overall]

        except Exception as e:
            print(f"Error during cluster-based recommendation for {customer_id}: {e}")
            recommendation_source = "Error during cluster processing; falling back to popularity"
            customer_cluster = "Error"
            cluster_recommendations = [] # Clear cluster recs on error
            final_overall_popular_recs = overall_top_products_global[:top_n_overall] # Fallback to unfiltered overall popular

    return {
        "customer_id": customer_id,
        "cluster": customer_cluster,
        "recommendation_source": recommendation_source,
        "cluster_based_recommendations": cluster_recommendations,
        "overall_popular_recommendations": final_overall_popular_recs,
        "r_score": customer_r_score,
        "f_score": customer_f_score,
        "m_score": customer_m_score,
        "rfm_segment_label": customer_rfm_segment_label,
        "purchased_products": purchased_products_current_customer # Include purchased products
    }

# --- Main execution for pipeline.py (if run directly for training/saving) ---
if __name__ == "__main__":
    print("Running data processing and model training pipeline...")
    df_orders_ca = load_and_preprocess_data()
    rfm_df = calculate_rfm(df_orders_ca)
    
    n_clusters_optimal_for_pipeline = 3 
    rfm_df, scaler, encoder, kmeans_latent, rfm_features_trained = score_rfm_and_cluster(rfm_df.copy(), n_clusters_optimal_for_pipeline)
    
    # Merge cluster IDs back to the original orders DataFrame
    df_orders_ca_with_clusters = pd.merge(
        df_orders_ca,
        rfm_df[['Customer ID', 'Cluster_AE']],
        on='Customer ID',
        how='left'
    )
    df_orders_ca_with_clusters.dropna(subset=['Cluster_AE'], inplace=True)
    df_orders_ca_with_clusters['Cluster_AE'] = df_orders_ca_with_clusters['Cluster_AE'].astype(int)

    save_models_and_data(rfm_df, df_orders_ca_with_clusters, scaler, encoder, kmeans_latent)
    print("Pipeline execution complete. Models and data saved.")