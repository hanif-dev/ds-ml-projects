# smart_retail_engine/scripts/app_tkinter.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import os
import sys

# Add the project root directory to the Python path to allow imports from 'scripts'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Flask API URL Configuration ---
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://localhost:5000")

class RecommendationApp:
    def __init__(self, master):
        self.master = master
        master.title("Smart Retail Recommender")
        master.geometry("650x700") # Adjust size for more content
        master.resizable(False, False)

        # --- Title ---
        self.label_title = tk.Label(master, text="🛍️ Smart Retail Recommendation Engine", font=("Arial", 18, "bold"))
        self.label_title.pack(pady=15)

        # --- Customer ID Input ---
        self.frame_input = tk.Frame(master)
        self.frame_input.pack(pady=10)

        self.label_customer_id = tk.Label(self.frame_input, text="Enter Customer ID:", font=("Arial", 10))
        self.label_customer_id.pack(side=tk.LEFT, padx=5)

        self.entry_customer_id = tk.Entry(self.frame_input, width=35, font=("Arial", 10))
        self.entry_customer_id.pack(side=tk.LEFT, padx=5)
        self.entry_customer_id.bind("<Return>", self.get_recommendations) # Allow Enter key to submit
        self.entry_customer_id.insert(0, "MW-18235") # Pre-fill for convenience

        self.button_recommend = tk.Button(master, text="Get Recommendations", command=self.get_recommendations, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
        self.button_recommend.pack(pady=15)

        # --- Output Results Frame ---
        self.frame_output = tk.LabelFrame(master, text="Recommendation Results", font=("Arial", 12, "bold"), padx=15, pady=15)
        self.frame_output.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Customer Info & Strategy
        self.label_customer_id_display = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10, "bold"))
        self.label_customer_id_display.pack(pady=2, anchor="w")
        
        self.label_cluster_info = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10))
        self.label_cluster_info.pack(pady=2, anchor="w")

        self.label_strategy_info = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10))
        self.label_strategy_info.pack(pady=2, anchor="w")

        # RFM Information
        tk.Label(self.frame_output, text="\n--- RFM Information ---", font=("Arial", 11, "underline")).pack(pady=5, anchor="w")
        self.label_rfm_r = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10))
        self.label_rfm_r.pack(pady=2, anchor="w")
        self.label_rfm_f = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10))
        self.label_rfm_f.pack(pady=2, anchor="w")
        self.label_rfm_m = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10))
        self.label_rfm_m.pack(pady=2, anchor="w")
        self.label_rfm_segment = tk.Label(self.frame_output, text="", justify=tk.LEFT, wraplength=550, font=("Arial", 10, "bold"))
        self.label_rfm_segment.pack(pady=2, anchor="w")

        # Purchased Products
        tk.Label(self.frame_output, text="\n--- Products You've Purchased ---", font=("Arial", 11, "underline")).pack(pady=5, anchor="w")
        self.text_purchased = scrolledtext.ScrolledText(self.frame_output, width=65, height=4, wrap=tk.WORD, font=("Arial", 9))
        self.text_purchased.pack(pady=5)

        # Personalized Recommendations
        tk.Label(self.frame_output, text="\n--- Personalized Recommendations ---", font=("Arial", 11, "underline")).pack(pady=5, anchor="w")
        self.text_personalized_recs = scrolledtext.ScrolledText(self.frame_output, width=65, height=4, wrap=tk.WORD, font=("Arial", 9))
        self.text_personalized_recs.pack(pady=5)

        # Overall Popular Recommendations
        tk.Label(self.frame_output, text="\n--- Overall Popular Products ---", font=("Arial", 11, "underline")).pack(pady=5, anchor="w")
        self.text_overall_popular_recs = scrolledtext.ScrolledText(self.frame_output, width=65, height=4, wrap=tk.WORD, font=("Arial", 9))
        self.text_overall_popular_recs.pack(pady=5)

        self._clear_output() # Clear outputs on startup

    def get_recommendations(self, event=None): # event=None for button click, event for Enter key
        customer_id = self.entry_customer_id.get().strip()
        if not customer_id:
            messagebox.showwarning("Empty Input", "Please enter a Customer ID.")
            return

        self._clear_output() # Clear previous results
        self.button_recommend.config(state=tk.DISABLED, text="Fetching...") # Disable button and show status

        try:
            response = requests.get(f"{FLASK_API_URL}/recommendations/{customer_id}")
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if "error" in data:
                messagebox.showerror("API Error", f"An error occurred: {data['error']}")
            else:
                self.label_customer_id_display.config(text=f"Customer ID: {data['customer_id']}")
                self.label_cluster_info.config(text=f"Autoencoder Cluster: {data.get('cluster', 'N/A')}")
                # Corrected key from 'source' to 'recommendation_source'
                self.label_strategy_info.config(text=f"Recommendation Strategy: {data.get('recommendation_source', 'N/A')}")

                # Populate RFM Information
                self.label_rfm_r.config(text=f"Recency Score: {data.get('r_score', 'N/A')}")
                self.label_rfm_f.config(text=f"Frequency Score: {data.get('f_score', 'N/A')}")
                self.label_rfm_m.config(text=f"Monetary Score: {data.get('m_score', 'N/A')}")
                self.label_rfm_segment.config(text=f"RFM Segment: {data.get('rfm_segment_label', 'N/A')}")

                # Populate Purchased Products
                purchased_text = "No purchase history found."
                if data.get('purchased_products'):
                    purchased_text = "\n".join([f"- {item}" for item in data['purchased_products']])
                self.text_purchased.delete(1.0, tk.END)
                self.text_purchased.insert(tk.END, purchased_text)

                # Populate Personalized Recommendations
                personalized_recs_text = "No personalized recommendations found."
                if data.get('cluster_based_recommendations'):
                    personalized_recs_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(data['cluster_based_recommendations'])])
                self.text_personalized_recs.delete(1.0, tk.END)
                self.text_personalized_recs.insert(tk.END, personalized_recs_text)

                # Populate Overall Popular Recommendations
                overall_popular_recs_text = "No overall popular recommendations available."
                if data.get('overall_popular_recommendations'):
                    overall_popular_recs_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(data['overall_popular_recommendations'])])
                self.text_overall_popular_recs.delete(1.0, tk.END)
                self.text_overall_popular_recs.insert(tk.END, overall_popular_recs_text)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to Flask API. Please ensure the API is running at "
                                 f"`{FLASK_API_URL}`.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred while fetching recommendations: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}. Check your Flask API response structure.")
        finally:
            self.button_recommend.config(state=tk.NORMAL, text="Get Recommendations") # Re-enable button

    def _clear_output(self):
        self.label_customer_id_display.config(text="")
        self.label_cluster_info.config(text="")
        self.label_strategy_info.config(text="")
        self.label_rfm_r.config(text="")
        self.label_rfm_f.config(text="")
        self.label_rfm_m.config(text="")
        self.label_rfm_segment.config(text="")
        self.text_purchased.delete(1.0, tk.END)
        self.text_personalized_recs.delete(1.0, tk.END)
        self.text_overall_popular_recs.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecommendationApp(root)
    root.mainloop()