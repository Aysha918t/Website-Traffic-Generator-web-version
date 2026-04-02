import asyncio
import random
import threading
import psutil
import time
import gradio as gr
import plotly.graph_objects as go
from playwright.async_api import async_playwright
from fake_useragent import UserAgent

# --- Configuration ---
TARGET_URL = "https://www.codestorez.com"
RAM_LIMIT_GB = 200
MIN_STAY = 15
MAX_STAY = 40
ua = UserAgent()

# --- Global Stats Store ---
stats = {
    "success": 0, 
    "fail": 0, 
    "active_browsers": 0, 
    "start_time": time.time(),
    "running": True
}

AD_BLOCK_PATTERNS = ["adsbygoogle.js", "doubleclick.net", "googleadservices.com", "/pagead/js/"]
SOCIAL_REFS = ["https://t.co/", "https://l.facebook.com/", "https://www.youtube.com/", "https://www.reddit.com/"]

async def run_instance():
    stats["active_browsers"] += 1
    async with async_playwright() as p:
        try:
            # High-performance launch (allowing RAM consumption)
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
            context = await browser.new_context(
                user_agent=ua.random,
                extra_http_headers={"Referer": random.choice(SOCIAL_REFS)}
            )
            
            # AdSense Shield
            await context.route("**/*", lambda route: 
                route.abort() if any(p in route.request.url.lower() for p in AD_BLOCK_PATTERNS) 
                else route.continue_()
            )
            
            page = await context.new_page()
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            
            # Engagement
            await page.mouse.wheel(0, random.randint(400, 1000))
            await asyncio.sleep(random.uniform(MIN_STAY, MAX_STAY))
            
            stats["success"] += 1
        except:
            stats["fail"] += 1
        finally:
            await browser.close()
            stats["active_browsers"] -= 1

async def hyper_engine():
    while stats["running"]:
        current_ram_gb = psutil.virtual_memory().used / (1024**3)
        if current_ram_gb < RAM_LIMIT_GB:
            # Spawn new tasks without blocking the loop
            asyncio.create_task(run_instance())
            await asyncio.sleep(0.02) # Extremely fast spawning
        else:
            await asyncio.sleep(1)

# --- Gradio UI Logic ---
def get_dashboard_data():
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    cpu_usage = psutil.cpu_percent()
    uptime = int(time.time() - stats["start_time"])
    
    # Status Markdown
    status_md = f"""
    ### ⚡ Engine Status: {'🟢 HYPER-SCALE' if stats['running'] else '⚪ IDLE'}
    **Uptime:** {uptime//60}m {uptime%60}s | **CPU Load:** {cpu_usage}%
    **Success:** {stats['success']} | **Failed:** {stats['fail']}
    **Active Browsers:** {stats['active_browsers']}
    """
    
    # RAM Gauge Chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = used_gb,
        title = {'text': f"System RAM (Target: {RAM_LIMIT_GB}GB)"},
        gauge = {
            'axis': {'range': [None, 256]},
            'bar': {'color': "#2563eb"},
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': RAM_LIMIT_GB}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(t=50, b=10))
    
    return status_md, fig

# --- UI Layout ---
light_ui_css = ".gradio-container {background-color: #f9fafb;} .stat-box {background: white; border-radius: 10px; padding: 15px; border: 1px solid #e5e7eb;}"

with gr.Blocks(css=light_ui_css, title="Taher IT Dashboard") as demo:
    gr.Markdown("# 🚀 TAHER IT - Mega Runner Console")
    
    with gr.Row(elem_classes="stat-box"):
        with gr.Column(scale=1):
            status_output = gr.Markdown("### Initializing...")
        with gr.Column(scale=2):
            gauge_output = gr.Plot()
            
    # Auto-refresh timer (Every 2 seconds)
    gr.Timer(value=2).tick(get_dashboard_data, outputs=[status_output, gauge_output])

# --- Entry Point ---
def run_all():
    # Start Engine in a separate thread
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: loop.run_until_complete(hyper_engine()), daemon=True).start()
    # Start Dashboard
    demo.launch(share=True, server_port=7860)

if __name__ == "__main__":
    run_all()
