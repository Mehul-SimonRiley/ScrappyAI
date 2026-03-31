import os
import re
import time
import random
import urllib.parse
from datetime import datetime
from collections import deque

import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Disable insecure request warnings when verify=False is used in requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup NLTK Data (Only download if necessary)
def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt_tab')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("[System] Downloading required NLTK datasets...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("[System] NLTK downloads complete.")

setup_nltk()

# The Independent `WebCrawler` autonomous URL HTTP-spider has been completely eradicated in V16.
# The system now strictly defaults to isolated `playwright` manual browser sequences natively.

class DataCleaner:
    """
    Processes raw HTML into clean, tokenized text suitable for LLMs using BeautifulSoup and NLTK.
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_html(self, raw_html):
        """Extract plain text from HTML while removing boilerplate."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove script, style, header, footer, and nav elements to reduce noise natively without collapsing DOM
        for script in soup.find_all(['script', 'style', 'noscript', 'meta']):
            script.decompose()
            
        # Separate by newlines to preserve page structure natively
        text = soup.get_text(separator='\\n', strip=True)
        return text

    def process_text_for_llm(self, text):
        """Use NLTK to clean text while preserving structure for modern LLMs."""
        cleaned_lines = []
        
        # Process line by line to maintain structure
        for line in text.split('\n'):
            line = line.strip()
            if len(line) < 3: # Skip empty or tiny artifacts
                continue
                
            # Word tokenization
            words = word_tokenize(line)
            # Remove stopwords but keep normal words and punctuation (LLMs need punctuation!)
            cleaned_words = [word for word in words if word.lower() not in self.stop_words]
            
            if cleaned_words:
                # Rejoin line and append
                cleaned_lines.append(" ".join(cleaned_words))
                
        # Join back together with newlines to preserve readability and structure!
        return "\n".join(cleaned_lines)

    def pipeline(self, raw_html_dict, logger=print):
        """Processes a dictionary of {url: raw_html} into {url: clean_text}."""
        logger("\\n[Cleaner] Starting data cleaning pipeline...")
        clean_data = {}
        for url, html in raw_html_dict.items():
            raw_text = self.clean_html(html)
            dense_text = self.process_text_for_llm(raw_text)
            if dense_text:
                clean_data[url] = dense_text
                
        logger(f"[Cleaner] Successfully cleaned {len(clean_data)} pages.")
        return clean_data


class SemanticFilter:
    """
    Chunks the giant NLTK-cleaned text corpus and uses dense embeddings
    to isolate only the blocks of text relevant to small user prompts.
    """
    def __init__(self, model_name="BAAI/bge-large-en-v1.5"):
        # We lazily import so it doesn't crash prior backend testing if uninstalled
        from sentence_transformers import SentenceTransformer
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.encoder = SentenceTransformer(model_name, device=device)

    def chunk_text(self, text, chunk_size=300):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def filter(self, prompt, text, top_k=15, logger=print):
        logger("\\n[SemanticFilter] Chunking scraped data...")
        chunks = self.chunk_text(text)
        if not chunks:
            return ""
        
        if len(chunks) <= top_k:
            return text

        logger(f"[SemanticFilter] Generating dense vector embeddings for {len(chunks)} HTML chunks...")
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        prompt_embedding = self.encoder.encode([prompt])
        chunk_embeddings = self.encoder.encode(chunks)
        
        similarities = cosine_similarity(prompt_embedding, chunk_embeddings)[0]
        
        # Get Top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        top_indices.sort() # Preserve chronological read order for the LLM
        
        filtered_context = ""
        # 8192 Token Context Firewall (~26,000 characters)
        for i in top_indices:
            next_chunk = "\\n...[SNIP]...\\n" + chunks[i]
            if len(filtered_context) + len(next_chunk) > 26000:
                logger("[SemanticFilter] Warning: Reached absolute context boundary limit. Truncating remainder to prevent crash.")
                break
            filtered_context += next_chunk
            
        logger(f"[SemanticFilter] Successfully compressed HTML context from {len(text)} down to {len(filtered_context)} characters of highly-relevant targeted context!")
        return filtered_context


def execute_scrape_only(target_url, logger=print):
    """V16 Stage 1: Browser-First Infinite Navigation and Scrape Payload Extraction."""
    logger(f"\\n[Stage 1: Browse] Initializing visible browser routing to {target_url}...")
    from playwright.sync_api import sync_playwright
    import time
    
    ejected_html = ""
    try:
        with sync_playwright() as p:
            # We strictly enforce headless=False so the User verifies the exact layout physically
            browser = p.chromium.launch(
                headless=False, 
                args=["--disable-http2", "--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
                ignore_https_errors=True
            )
            page = context.new_page()
            
            logger(f"[Visible Engine] Loading target page: {target_url}")
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
            except Exception as pg_err:
                logger(f"[Stealth Engine] Network stall isolated. Awaiting manual user navigation: {pg_err}")
                
            logger("[Stealth Engine] Browser launched securely! Handing Navigation Control to Human Operator...")
            logger("   -> [Alert] Navigate to your target layout internally, then click the floating ✅ Button to capture data!")
            
            while True:
                try:
                    # Dynamically re-inject the target button natively across user navigations
                    page.evaluate("""
                        () => {
                            if (!document.getElementById('scrappy-btn')) {
                                window.scraperConfirmed = false;
                                const btn = document.createElement('button');
                                btn.id = 'scrappy-btn';
                                btn.innerText = '✅ Extract This Page';
                                btn.style.position = 'fixed';
                                btn.style.bottom = '20px';
                                btn.style.right = '20px';
                                btn.style.zIndex = '2147483647';
                                btn.style.padding = '12px 24px';
                                btn.style.fontSize = '14px';
                                btn.style.fontWeight = 'bold';
                                btn.style.backgroundColor = '#0066ff';
                                btn.style.color = 'white';
                                btn.style.border = '1px solid white';
                                btn.style.borderRadius = '5px';
                                btn.style.cursor = 'pointer';
                                btn.style.boxShadow = '0 4px 12px rgba(0,0,0,0.4)';
                                btn.style.fontFamily = 'Arial, sans-serif';
                                
                                btn.onclick = () => {
                                    window.scraperConfirmed = true;
                                    btn.innerText = '⏳ Extracting...';
                                    btn.style.backgroundColor = '#00b347';
                                };
                                document.body.appendChild(btn);
                            }
                        }
                    """)
                    
                    # Poll the Javascript boolean trigger securely
                    if page.evaluate("window.scraperConfirmed"):
                        logger("\\n[Stealth Engine] Scrape Target Mathematically Verified by User via DOM Click!")
                        page.evaluate("document.getElementById('scrappy-btn').remove()")
                        break
                        
                except Exception: # Target navigated context reset
                    pass
                time.sleep(1.0)
                
            # Post-authorization Infinite Scroll Engine natively targeting payload structures
            logger("[Scroll Engine] Forcefully scrolling physical browser to trigger DOM ejections...")
            last_height = page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            
            while scroll_attempts < 25:
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(0.5) 
                
                try:
                    page.wait_for_load_state("networkidle", timeout=3000)
                except Exception:
                    pass
                    
                is_bottom = page.evaluate("(window.innerHeight + window.scrollY) >= document.body.scrollHeight - 20")
                if is_bottom:
                    time.sleep(5.0) # V13: Extended Lazy-Load Buffer!
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        logger("   -> [Smart Scroller] Viewport reached Absolute DOM floor. End of Infinite Array confirmed.")
                        break
                    last_height = new_height
                    
                scroll_attempts += 1
                logger(f"   -> [Scroll {scroll_attempts}/25] Pushing payload bounds smoothly downwards.")
                
            ejected_html = page.content()
            browser.close()
            
    except Exception as e:
        logger(f"[Error] Visual Scrape Sequence failed to launch: {str(e)}")
        return {"success": False, "error": str(e)}

    # Phase 2: Native Clean and File Dump
    logger(f"\\n[Scroll Engine] Stabilized. Captured dynamically loaded payload ({len(ejected_html)} bytes).")
    
    cleaner = DataCleaner()
    clean_text_dict = cleaner.pipeline({target_url: ejected_html}, logger=logger)
    clean_text = clean_text_dict.get(target_url, "")
    
    raw_debug_filepath = "raw_debug_output.txt"
    clean_debug_filepath = "scraped_debug_output.txt"
    try:
        with open(raw_debug_filepath, "w", encoding="utf-8") as f:
            f.write(ejected_html)
        with open(clean_debug_filepath, "w", encoding="utf-8") as f:
            f.write(clean_text)
        logger(f"   -> [Debug] Dumped {len(ejected_html)} byte raw DOM and Clean Tokens to purely offline logs natively.")
    except Exception as e:
        logger(f"   -> [Debug Warning] Could not write offline cache: {e}")

    # Return the clean text entirely for Stage 2 operations
    return {"success": True, "clean_text": clean_text}


def execute_llm_extraction(prompt, clean_text, semantic_filter, logger=print):
    """V16 Stage 2: Offline Generative AI Evaluation Array."""
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import json
    
    logger(f"\\n[Stage 2: Offline Target Extraction] Beginning Native Evaluation on Cached Corpus...")
    
    # Compress massive array bounds mathematically if necessary
    if semantic_filter and len(clean_text) > 3500:
        logger("\\n[SemanticFilter] Compressing massive data payload to fit LLM window...")
        try:
            clean_text = semantic_filter.filter(prompt, clean_text, top_k=20, logger=logger)
        except Exception as se:
            logger(f"   -> [SemanticFilter Crash] Skipping vector ranker: {se}")
            clean_text = clean_text[:3500]
    else:
        clean_text = clean_text[:3500]

    logger(f"\\n[Local AI] Booting 'google/flan-t5-base' on GPU for final contextual analysis...")
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        llm = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base").to(device)
        
        # Format the native instruction command string directly
        llm_prompt = f"Information to extract: {prompt}\\nSource block: {clean_text}\\nAnswer cleanly:"
        
        inputs = tokenizer(llm_prompt, return_tensors="pt", max_length=1024, truncation=True).to(device)
        outputs = llm.generate(**inputs, max_new_tokens=400)
        clean_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Purge tensors instantly
        del llm
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger("   -> [Local AI] Global Context evaluated natively! Returning final payload.")
        return json.dumps([{"Response": clean_output}], indent=2)
        
    except Exception as e:
        logger(f"[Local AI Error] Execution crashed: {e}")
        return json.dumps([{"Error": str(e)}])

def run_demo():
    """Main execution pipeline executing the Crawler -> Cleaner -> LLM loop."""
    print("="*50)
    print(" GENERAL PURPOSE WEB CRAWLER & LLM SCRAPER PIPELINE")
    print("="*50)
    
    # 1. Configuration - Ask User for Input
    print("\\n--- Configuration ---")
    TARGET_WEBSITE = input("Enter the starting URL to crawl (e.g., https://example.com): ").strip()
    
    if not TARGET_WEBSITE.startswith("http"):
        TARGET_WEBSITE = "https://" + TARGET_WEBSITE
        
    max_pages_to_crawl = 200
    USER_PROMPT = "Extract all main services and contact information from this website."
    
    # Run the pipeline
    answer, context = run_pipeline(TARGET_WEBSITE, USER_PROMPT, max_pages_to_crawl, logger=print)
    
    # Save context for review in console mode
    debug_filename = "cleaned_context_demo.txt"
    with open(debug_filename, "w", encoding="utf-8") as f:
        f.write(context)
        
    print(f"\\n[System] Saved the raw, cleaned NLTK data to '{debug_filename}' for review.")
    print("--- SNIPPET OF CLEANED DATA FOR QWEN 2.5 ---")
    print(context[:500] + "...\\n(See file for full text)\\n")
    
    print("\\n" + "="*50)
    print(" FINAL SYSTEM OUTPUT")
    print("="*50)
    print(answer)
    print("="*50)


if __name__ == "__main__":
    run_demo()
