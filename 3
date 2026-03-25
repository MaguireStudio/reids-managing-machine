import os
import requests
from apify_client import ApifyClient
import time

# Initialize the ApifyClient with your provided API token
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "apify_api_SFQVbC9fSvcdZzdgTL6Rlj2LqnMAMu3DQivM")
client = ApifyClient(APIFY_API_TOKEN)

WEBHOOK_URL = "http://localhost:8000/webhook/new_lead"

def scrape_airbnb_leads(location="San Diego, CA", max_results=5):
    """
    Triggers an Apify Actor to organically scrape Airbnb for listings without getting blocked.
    """
    print(f"Starting Apify Scraper for Airbnb listings in {location}...")
    
    # Run the popular Airbnb scraper actor: dtrungtin/airbnb-scraper
    run_input = {
        "locationQuery": location,
        "maxListings": max_results,
        "calendarMonths": 0,
        "currency": "USD"
    }

    try:
        # Run the Actor and wait for it to finish (Runs securely in Apify Cloud)
        print("Calling Apify Cloud (bypassing Cloudflare/CAPTCHAs - this may take a minute)...")
        run = client.actor("dtrungtin/airbnb-scraper").call(run_input=run_input)
        
        # Fetch and process Actor results from the dataset
        leads_processed = 0
        print("Scraping complete! Pulling dataset...")
        
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            # Extract lead data
            host_name = item.get("primaryHost", {}).get("hostName", "Unknown Airbnb Host")
            property_name = item.get("name", "Airbnb Property")
            listing_url = item.get("url", f"https://www.airbnb.com/rooms/{item.get('id')}")
            
            # Format the payload for our Mission Control webhook
            lead_payload = {
                "name": f"{host_name}",
                "phone": "+1-AIRBNB-HOST", # Placeholder: Airbnb hosts require messaging via platform
                "source": "Airbnb Scraper",
                "property_url": listing_url,
                "property_name": property_name,
                "pitch": "ROI Boost - Add a Hot Tub"
            }
            
            # Send to our Engine
            print(f"Pushing Lead to Mission Control: {host_name}...")
            response = requests.post(WEBHOOK_URL, json=lead_payload)
            if response.status_code in [200, 201]:
                leads_processed += 1
                
        print(f"\n✅ Successfully pushed {leads_processed} leads into the Mission Control Dashboard!")
            
    except Exception as e:
        print(f"Apify Scraping Failed: {e}")

if __name__ == "__main__":
    # Test run the scraper for 3 results to verify the pipeline
    scrape_airbnb_leads(location="San Diego, CA", max_results=3)
