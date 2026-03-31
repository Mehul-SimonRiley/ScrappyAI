import os
import sys
import io
import json
import threading
import webview
import time

# Globally force UTF-8 Terminal Stream Encoding to prevent PyInstaller Windows charmap crashes
class DummyStream:
    def write(self, *args, **kwargs): pass
    def flush(self, *args, **kwargs): pass
    
try:
    if sys.stdout is None or getattr(sys.stdout, 'closed', True):
        sys.stdout = DummyStream()
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
    if sys.stderr is None or getattr(sys.stderr, 'closed', True):
        sys.stderr = DummyStream()
    else:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

def safe_print(*args, **kwargs):
    """Fallback secure logger for unmapped visual binaries."""
    try:
        import sys
        
        # If running in --noconsole mode, stdout might be completely None or explicitly closed.
        if sys.stdout is None or getattr(sys.stdout, 'closed', True):
            return
            
        sys.stdout.write(" ".join(map(str, args)) + kwargs.get("end", "\\n"))
        sys.stdout.flush()
    except Exception:
        pass

import builtins
builtins.print = safe_print
import requests
import urllib.parse

# Import our decoupled V18 multi-model backend architecture routines
from backend.crawler_ex import execute_scrape_only, execute_nlp_extraction, execute_generative_fallback

class BackendApi:
    """
    This class is exposed directly to the JavaScript frontend.
    Methods here are callable via `window.pywebview.api.methodName()`
    """
    def __init__(self):
        self._window = None
        self.semantic_filter = None
        self.llm = None
        self._auth_event = threading.Event()
        self._auth_result = False

    def trigger_auth_modal(self):
        """Called python-side. Pauses execution and pops HTML modal in JS."""
        self._auth_event.clear()
        if self._window:
            self._window.evaluate_js("if(typeof showAuthModal === 'function') { showAuthModal(); }")
        self._auth_event.wait() # Physical block until user clicks JS button
        return self._auth_result

    def respond_auth(self, result):
        """Called JS-side when a user clicks the HTML Modal button."""
        self._auth_result = bool(result)
        self._auth_event.set()

    def set_window(self, window):
        self._window = window

    def log(self, message):
        """Allows JS to log to the Python console."""
        print(f"[Frontend JS] {message}")

    def is_valid_url_format(self, url):
        parsed = urllib.parse.urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def update_status(self, text, progress_percent=None):
        if self._window:
            safe_text = text.replace("'", "\\'")
            js_code = f"document.getElementById('loading-title').innerHTML = '{safe_text} <span class=\"dots\">...</span>';"
            if progress_percent is not None:
                js_code += f"document.querySelector('.progress-bar-fill').style.width = '{progress_percent}%';"
            self._window.evaluate_js(js_code)

    def start_scraping(self, url):
        """
        V16 Stage 1: Initiates visual browser session natively.
        Called by JS when the 'Open Browser & Scrape' button is pressed.
        """
        print(f"\\n[Backend API] Received Visual Scrape Target for Domain: {url}")
        
        # 1. Server-side validation
        if not url.startswith("http"):
            url = "https://" + url

        if not self.is_valid_url_format(url):
            return {"success": False, "error": "Invalid URL format. Provide a full domain."}

        # 2. Fast HTTP Head Check to prevent locking UI on fake domains
        self.update_status("Verifying HTTP Response Server", 5)
        try:
            # Modern browsers mimic to bypass basic Cloudflare/Imperva filters
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            resp = requests.head(url, timeout=5, allow_redirects=True, verify=False, headers=headers)
            
            # Explicitly ignore 403/401/405 (Cloudflare/Bot Protections) and let Playwright stealth engine handle it
            if resp.status_code >= 400 and resp.status_code not in [401, 403, 405]:
                resp = requests.get(url, timeout=5, stream=True, verify=False, headers=headers)
                if resp.status_code >= 400 and resp.status_code not in [401, 403, 405]:
                    return {"success": False, "error": f"Server rejected connect (HTTP {resp.status_code})."}
        except requests.exceptions.RequestException:
            # If the library crashes completely (IP Ban or tight Firewall), we gracefully Pass to the Playwright Native Engine anyway
            pass

        def custom_logger(msg):
            print(msg)
            # Route custom backend logs directly into the PyWebView Javascript DOM
            if "[Crawler] Starting GUI Headless" in msg:
                self.update_status("Bypassing Defenses & Crawling", 15)
            elif "[Crawler] Warming up Chromium" in msg:
                self.update_status("Booting Headless Web Browser", 30)
            elif "[Smart Scout]" in msg:
                self.update_status("AI Analyzing DOM Structure (Smart Scout)", 50)
            elif "[Fast Scrape]" in msg:
                self.update_status("Fast Scraping 100+ Pages natively...", 80)
            elif "Extracting raw text natively via DataCleaner for maximum speed" in msg:
                self.update_status("NLP Fallback: Stripping HTML natively...", 60)
            elif "[Backend API] Scraping completed" in msg:
                self.update_status("Packaging final Native Data Stream", 95)

        try:
            # V16 Fast Stage 1 Execution
            self.update_status("Opening Manual Navigation Window", 30)
            
            result_dict = execute_scrape_only(
                target_url=url,
                logger=custom_logger
            )
            
            if not result_dict.get("success"):
                return {"success": False, "error": result_dict.get("error", "Unknown Fetch Error")}
                
            # Persist pure clean corpus deeply in memory for fast offline AI Stage 2 Prompts!
            self._last_corpus = result_dict.get("clean_text", "")
            
            if not self._last_corpus.strip():
                return {"success": False, "error": "Unable to extract text nodes natively. DOM might have been empty."}
                
            self.update_status("Processing Advanced NLP Extraction natively...", 90)
            
            # Immediately run the NLP structure mapping natively (Stage 2)
            answer_json = execute_nlp_extraction(
                clean_text=self._last_corpus,
                logger=safe_print
            )
            
            # Store structural mapping natively for fallback AI routing securely
            self._last_json = answer_json
            
            self.update_status("Finalizing Response", 100)
            safe_print("[Backend API] Scrape & Extract successfully completed natively.")
            
            # UI Masking: Hide the raw JSON dictionary and invite the User to trigger Stage 3 Generative Fallback
            ui_response = json.dumps([{
                "Generated_Insight": "### 🚀 Data Extraction Complete!\\n\\nI have successfully scraped and structurally cached all targeted contexts from the website entirely offline! Your payload is securely loaded in system memory.\\n\\n**Please type your analytical prompt into the textbox below** (e.g., *'Extract all restaurant reviews'*) to execute the Qwen Fallback reasoning engine over this specific payload!"
            }])
            
            return {"success": True, "answer": ui_response}
            
        except Exception as e:
            return {"success": False, "error": f"Fatal Backend Operations Error: {str(e)}"}

    def execute_ai_query(self, text):
        """V18 Stage 3: Generative LLM Fallback interaction using Qwen."""
        if not hasattr(self, '_last_json') or not self._last_corpus:
            return '[{"Error": "System Error: No baseline corpus mapping found. Please deploy Stage 1 Scraper first."}]'
            
        print(f"\\n[Backend API] Evaluating Custom User Prompt against Qwen Fallback: '{text}' natively...\\n")
        
        # Execute Offline Inference on Local Generative Tensors natively using structured JSON
        answer_json = execute_generative_fallback(
            prompt=text,
            structured_data_json=self._last_json,
            raw_text=self._last_corpus,
            logger=safe_print
        )
        
        return answer_json

def resource_path(relative_path):
    """ Dynamically route assets to support PyInstaller temp C: bounds natively. """
    try:
        # PyInstaller extracts to _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    api = BackendApi()
    
    # Path to our new modern Web UI mathematically linked to PyInstaller resources
    html_path = resource_path(os.path.join('frontend', 'index.html'))
    
    # Create the native desktop window wrapping our HTML
    window = webview.create_window(
        'ScrappyAI - Enterprise Desktop Interface', 
        url=html_path, # Provide raw path, PyWebView handles it
        js_api=api,
        width=1100, 
        height=720,
        min_size=(900, 600),
        background_color='#f7f8fa', # Matches light theme base
        text_select=True,
    )
    api.set_window(window)
    
    def on_closed():
        safe_print("[System] Desktop Window Closed. Terminating background CUDA threads instantly...")
        import os
        os._exit(0) # Brutally and safely kill all C++ inferencing threads to prevent ghost processes
        
    window.events.closed += on_closed
    
    safe_print("[System] Starting PyWebView Desktop GUI using internal HTTP Server...")
    # Start the application loop with http_server to resolve local CSS/JS correctly
    # Disable DevTools popup completely in Production Desktop Application!
    webview.start(debug=False, http_server=True)

if __name__ == '__main__':
    main()
