import os
import requests

GHL_API_KEY = os.getenv("GHL_API_KEY", "YOUR_GHL_API_KEY_HERE")
NURTURE_TAG = "ai_unqualified_nurture"

def enroll_in_nurture_campaign(lead_name: str, lead_phone: str, lead_email: str = None):
    """
    Pushes the lead into GoHighLevel and tags them to trigger a 30-day SMS/Email nurture sequence.
    """
    url = "https://services.leadconnectorhq.com/contacts/"
    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    # Split name into First and Last for typical CRM formats
    names = lead_name.split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""
    
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "phone": lead_phone,
        "tags": [NURTURE_TAG], # This tag triggers the workflow in GHL
        "source": "Speed-to-Lead Engine"
    }
    
    if lead_email:
        payload["email"] = lead_email
        
    print(f"Pushing {lead_name} to GoHighLevel with Nurture Tag...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        print("Successfully enrolled in GHL Nurture Campaign.")
        return response.json()
    else:
        print(f"Failed to push to GHL: {response.text}")
        return None
