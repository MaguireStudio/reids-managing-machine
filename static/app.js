// App Dashboard JS Logic
function switchTab(sectionId, tabId) {
    document.getElementById('leads-section').classList.add('hidden');
    document.getElementById('inbox-section').classList.add('hidden');
    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    
    document.getElementById(sectionId).classList.remove('hidden');
    document.getElementById(tabId).classList.add('active');
}

async function refreshLeads() {
    try {
        const res = await fetch('/api/leads');
        const data = await res.json();
        
        const tbody = document.getElementById('leads-table-body');
        tbody.innerHTML = '';
        
        let qualified = 0;
        let transfers = 0;
        
        if (data.leads.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-muted);padding:2rem;">No leads detected. Awaiting webhooks from Zapier.</td></tr>';
        }

        data.leads.forEach(lead => {
            if (lead.status === 'qualified') { qualified++; transfers++; }

            const tr = document.createElement('tr');
            let badgeClass = 'pending';
            let badgeText = 'Awaiting AI Response';
            
            if (lead.status === 'qualified') {
                badgeClass = 'qualified'; badgeText = 'Live Transfer (Hot)';
            } else if (lead.status === 'nurture') {
                badgeClass = 'nurture'; badgeText = 'CRM Nurture (Cold)';
            }

            tr.innerHTML = `
                <td style="font-weight:600; color:#fff;">${lead.name}</td>
                <td style="font-family:monospace; color:var(--text-muted)">${lead.phone}</td>
                <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                <td style="color:var(--text-muted)">${new Date(lead.time).toLocaleTimeString()}</td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('val-leads').innerText = data.leads.length;
        document.getElementById('val-transfers').innerText = transfers;
        
        const qualRate = data.leads.length > 0 ? Math.round((qualified / data.leads.length) * 100) : 0;
        document.getElementById('val-qual').innerText = `${qualRate}%`;

    } catch (err) {
        console.error("Failed to load leads", err);
    }
}

async function refreshInbox() {
    try {
        const res = await fetch('/api/messages');
        const data = await res.json();
        
        const feed = document.getElementById('chat-feed-box');
        
        if (data.messages.length === 0) {
            feed.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding: 3rem;">No incoming messages yet. Awaiting Zapier webhooks inside GHL.</div>';
            return;
        }

        feed.innerHTML = '';
        data.messages.forEach(msg => {
            const div = document.createElement('div');
            const typeClass = msg.type.toLowerCase() === 'email' ? 'email' : 'sms';
            
            div.className = `chat-msg ${typeClass}`;
            div.innerHTML = `
                <div class="chat-meta">
                    <div><span class="chat-name">${msg.name}</span> <span style="margin-left: 10px; opacity: 0.6;">${msg.phone}</span></div>
                    <div style="display:flex; align-items:center; gap: 15px;">
                        <span class="chat-type ${typeClass}">${msg.type}</span>
                        <span>${new Date(msg.time).toLocaleTimeString()}</span>
                    </div>
                </div>
                <div class="chat-content">${msg.content}</div>
            `;
            feed.appendChild(div);
        });
    } catch (e) { console.error("Inbox load failed", e); }
}

function toggleSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.toggle('hidden');
    if (!modal.classList.contains('hidden')) {
        fetch('/api/settings').then(r => r.json()).then(s => {
            document.getElementById('set-vapi').value = s.VAPI_API_KEY || '';
            document.getElementById('set-ghl').value = s.GHL_API_KEY || '';
            document.getElementById('set-transfer').value = s.AGENT_TRANSFER_NUMBER || '';
        });
    }
}

async function saveSettings() {
    const payload = {
        VAPI_API_KEY: document.getElementById('set-vapi').value,
        GHL_API_KEY: document.getElementById('set-ghl').value,
        AGENT_TRANSFER_NUMBER: document.getElementById('set-transfer').value
    };

    const btn = document.querySelector('button[type="submit"]');
    const ogText = btn.innerText;
    btn.innerText = "Arming Engine...";
    
    await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    setTimeout(() => {
        btn.innerText = ogText;
        toggleSettings();
    }, 500);
}

// Bot Mechanics
function toggleChat() {
    document.getElementById('chat-widget').classList.toggle('hidden');
}

async function handleCommandChat(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('command-input');
        const msg = input.value.trim();
        if (!msg) return;
        
        input.value = '';
        appendCommandMessage('user', msg);
        
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            appendCommandMessage('bot', data.response);
        } catch (e) {
            appendCommandMessage('bot', 'System Error: Backend offline or unreachable.');
        }
    }
}

function appendCommandMessage(sender, text) {
    const container = document.getElementById('command-messages');
    const div = document.createElement('div');
    div.className = sender === 'user' ? 'user-msg' : 'bot-msg';
    div.innerText = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Global Pollers
refreshLeads();
refreshInbox();
setInterval(() => {
    refreshLeads();
    refreshInbox();
}, 2000);
