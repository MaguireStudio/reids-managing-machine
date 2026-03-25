import os
import requests

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "YOUR_VAPI_KEY_HERE")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID", "YOUR_ASSISTANT_ID_HERE")
AGENT_TRANSFER_NUMBER = os.getenv("AGENT_TRANSFER_NUMBER", "+1234567890")

def trigger_vapi_call(lead_name: str, lead_phone: str):
    """
    Triggers an outbound AI call via Vapi within 30 seconds of form submission.
    """
    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Payload configuring the AI Assistant mapping and prompt overrides
    payload = {
        "assistantId": VAPI_ASSISTANT_ID,
        "customer": {
            "number": lead_phone,
            "name": lead_name
        },
        "assistantOverrides": {
            "variableValues": {
                "LeadName": lead_name,
                "TransferNumber": AGENT_TRANSFER_NUMBER
            }
        }
    }
    
    print(f"Triggering Voice AI for {lead_name} at {lead_phone}...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        print("Success! Vapi call initiated.")
        return response.json()
    else:
        print(f"Failed to trigger call: {response.text}")
        return None
