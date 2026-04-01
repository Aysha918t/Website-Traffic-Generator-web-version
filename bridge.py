import os
import threading
import gradio as gr
import time

# 1. Start the actual Traffic Generator in the background
def run_app():
    os.system("python app.py")

threading.Thread(target=run_app, daemon=True).start()

# 2. Wait a moment for Flask to boot up on port 5000
time.sleep(5)

# 3. Create a Gradio interface that acts as a gateway
# This redirects the Gradio public URL to your local port 5000
with gr.Blocks() as demo:
    gr.Markdown("# Website Traffic Generator Gateway")
    gr.HTML('<iframe src="http://localhost:5000" width="100%" height="800px"></iframe>')

demo.launch(share=True)
