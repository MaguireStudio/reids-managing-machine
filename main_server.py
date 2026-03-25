from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import time
import json
import os
from vapi_trigger import trigger_vapi_call
from ghl_webhook import enroll_in_nurture_campaign
from apify_scraper import scrape_airbnb_leads

app = FastAPI(title="Speed-to-Lead Webhook Server")

# Serve specific static files natively
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory database for testing display
db = {
    "leads": [],
    "messages": [],
    "settings": {
        "VAPI_API_KEY": "",
        "GHL_API_KEY": "",
        "AGENT_TRANSFER_NUMBER": ""
    }
}

@app.get("/")
async def serve_dashboard():
    return FileResponse('static/index.html')

@app.get("/api/leads")
async def get_leads():
    return {"leads": list(reversed(db["leads"]))}

@app.get("/api/settings")
async def get_settings():
    return db["settings"]

@app.post("/api/settings")
async def save_settings(request: Request):
    data = await request.json()
    db["settings"].update(data)
    
    os.environ["VAPI_API_KEY"] = db["settings"].get("VAPI_API_KEY", "")
    os.environ["GHL_API_KEY"] = db["settings"].get("GHL_API_KEY", "")
    os.environ["AGENT_TRANSFER_NUMBER"] = db["settings"].get("AGENT_TRANSFER_NUMBER", "")
    
    return {"status": "saved"}

@app.post("/api/chat")
async def handle_chat(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    message = data.get("message", "").strip()
    
    if message.startswith("/scrape"):
        location = message.replace("/scrape", "").strip()
        if not location:
            location = "San Diego, CA"
        
        # Trigger the Scraper Actor
        background_tasks.add_task(scrape_airbnb_leads, location, 3)
        return {"response": f"Executing Apify Scraper protocol for '{location}'. Processing bypass. Leads will appear in the dashboard shortly!"}
        
    elif message.startswith("/call"):
        phone = message.replace("/call", "").strip()
        if not phone:
            return {"response": "Please specify a phone number to call. Format: `/call +1234567890`"}
        
        # Fire test lead into our system to trigger the loop
        lead_name = "Bot Direct Command"
        lead_record = {
            "id": str(time.time()),
            "name": lead_name,
            "phone": phone,
            "status": "pending",
            "time": time.time() * 1000
        }
        db["leads"].append(lead_record)
        
        # Fire Vapi Trigger natively
        background_tasks.add_task(trigger_vapi_call, lead_name, phone)
        
        return {"response": f"Deploying Voice AI agent to {phone}. Initiating outbound sequence."}
        
    else:
        return {"response": "Command not recognized. Please use `/scrape [target]` or `/call [phone]`."}

@app.post("/webhook/new_lead")
async def handle_new_lead(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    lead_name = data.get("name", "Unknown Lead")
    lead_phone = data.get("phone")
    
    if not lead_phone:
        return {"status": "error", "message": "Phone number is required."}
        
    print(f"\\n[ALERT] New Lead Received: {lead_name}")
    
    lead_record = {
        "id": str(time.time()),
        "name": lead_name,
        "phone": lead_phone,
        "status": "pending",
        "time": time.time() * 1000
    }
    db["leads"].append(lead_record)
    
    background_tasks.add_task(trigger_vapi_call, lead_name, lead_phone)
    
    return {"status": "success", "message": "Lead ingested and Voice AI triggered.", "lead": lead_record}


@app.post("/webhook/vapi_call_status")
async def handle_vapi_status(request: Request):
    data = await request.json()
    
    call_status = data.get("message", {}).get("call", {}).get("status")
    analysis = data.get("message", {}).get("analysis", {})
    
    is_budget_met = analysis.get("budget_over_800k", False)
    is_pre_approved = analysis.get("is_pre_approved", False)
    buying_in_90_days = analysis.get("buying_90_days", False)
    
    lead_phone = data.get("message", {}).get("customer", {}).get("number")
    
    target_lead = next((l for l in db["leads"] if l["phone"] == lead_phone), None)
    
    if is_budget_met and is_pre_approved and buying_in_90_days:
        if target_lead:
            target_lead["status"] = "qualified"
    else:
        if target_lead:
            target_lead["status"] = "nurture"
            
        if lead_phone:
            enroll_in_nurture_campaign(lead_name="Unknown Lead", lead_phone=lead_phone)
        
    return {"status": "received"}

@app.get("/api/messages")
async def get_messages():
    return {"messages": list(reversed(db["messages"]))}

@app.post("/webhook/inbound_msg")
async def handle_inbound_msg(request: Request):
    data = await request.json()
    msg_record = {
        "id": str(time.time()),
        "name": data.get("name", "Unknown Contact"),
        "phone": data.get("phone", ""),
        "type": data.get("type", "SMS"),
        "content": data.get("content", ""),
        "time": time.time() * 1000
    }
    db["messages"].append(msg_record)
    print(f"\\n[INBOX] New {msg_record['type']} from {msg_record['name']}: {msg_record['content'][:50]}...")
    return {"status": "success", "message": "Saved to Inbox"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
