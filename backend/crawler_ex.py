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
        """Extract clean, properly delimited text from HTML without destroying structure."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove massive structural noise
        for script in soup.find_all(['script', 'style', 'noscript', 'meta', 'svg', 'header', 'footer']):
            script.decompose()
            
        # Extract text with explicit visual block separation
        text = soup.get_text(separator=' \\n ', strip=True)
        return text

    def process_text_for_llm(self, text):
        """Clean extra spacings natively."""
        import re
        # Convert literal \n representations and extra spaces to normal layout
        text = text.replace('\\n', ' \n ')
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def pipeline(self, raw_html_dict, logger=print):
        """Processes a dictionary of {url: raw_html} into {url: clean_text}."""
        logger("\\n[Cleaner] Starting pristine structural cleaning pipeline (No stopword mangling)...")
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
            try:
                browser = p.chromium.launch(
                    channel="msedge",
                    headless=False, 
                    args=["--disable-http2", "--disable-blink-features=AutomationControlled"]
                )
            except Exception:
                try:
                    logger("[Stage 1: Browse] Native Edge unavailable. Hooking into Google Chrome globally...")
                    browser = p.chromium.launch(
                        channel="chrome",
                        headless=False, 
                        args=["--disable-http2", "--disable-blink-features=AutomationControlled"]
                    )
                except Exception:
                    logger("[Stage 1: Browse] Native OS browsers unavailable. Falling back to Playwright Internal Chromium...")
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
                
            # Ultra-slow crawling Engine natively targeting payload structures
            logger("[Scroll Engine] Forcefully scrolling physical browser to trigger deep DOM lazy loads...")
            last_height = page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            
            # Very small, incredibly gradual scrolling to ensure JS lazy-loaded content correctly fires
            while scroll_attempts < 120:
                page.evaluate("window.scrollBy(0, 200)")  # Dropped from 400px to 200px
                time.sleep(0.8)  # Doubled wait time per micro-scroll
                
                try:
                    page.wait_for_load_state("networkidle", timeout=1000)
                except Exception:
                    pass
                    
                is_bottom = page.evaluate("(window.innerHeight + window.scrollY) >= document.body.scrollHeight - 30")
                if is_bottom:
                    time.sleep(3.0) # Extended Lazy-Load Buffer!
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height <= last_height + 50:
                        logger("   -> [Smart Scroller] Viewport reached Absolute DOM floor. End of Infinite Array confirmed.")
                        break
                    last_height = new_height
                    
                scroll_attempts += 1
                if scroll_attempts % 10 == 0:
                    logger(f"   -> [Scroll {scroll_attempts}/120] Pushing payload bounds smoothly downwards.")
                
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


def execute_nlp_extraction(clean_text, logger=print):
    """V18 Stage 2: Advanced NLP Extractor Pipeline (Regex + spaCy mapping natively)"""
    import json
    import time
    import re
    
    logger(f"\\n[Stage 2: Automatic NLP Extraction] Bypassing Generative LLM for pure structural parsing natively...")
    start_time = time.time()
    
    try:
        import spacy
        try:
            logger("   -> Booting spaCy 'en_core_web_sm' NER engine...")
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger("   -> Booting failed: downloading 'en_core_web_sm' model natively...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
            
        doc = nlp(clean_text[:100000]) # Cap size to 100k for performance
        
        # 1. Advanced Structural Entity Detection
        entity_counts = {}
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON', 'FAC'] and len(ent.text.strip()) > 2:
                # Completely strip \n, | and / tags natively
                clean_ent = re.sub(r'[\n\r]+|\\n', ' ', ent.text)
                clean_ent = re.sub(r'[\/\|]', '', clean_ent)
                clean_ent = re.sub(r'\s+', ' ', clean_ent).strip()
                
                # Filter out pure garbage and isolated numbers universally
                if len(clean_ent) > 3 and not re.match(r'^[\d\s\W]+$', clean_ent):
                    entity_counts[clean_ent] = entity_counts.get(clean_ent, 0) + 1
                    
        # Sort entities by frequency to get the most important topics on the page
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        top_entities = [ent[0] for ent in sorted_entities[:15]]
        
        # 2. Universal Sentence Filtering (Mathematically separating content from pure UI noise generically for ANY site)
        valid_content_blocks = []
        for sent in doc.sents:
            text = sent.text.strip()
            
            # Universal text cleanup for the sentence block
            text_clean = re.sub(r'[\n\r]+|\\n', ' ', text)
            text_clean = re.sub(r'\s+[\/\|\,]\s+', ', ', text_clean) # Convert stray slashes to commas
            text_clean = re.sub(r'\s+', ' ', text_clean).strip()
            
            # Universal Validation: A real sentence usually has at least 5 words and contains alphabetic logic
            words = text_clean.split()
            if len(words) >= 4:
                # Measure alphanumeric density to reject isolated UI button arrays (e.g. "1 2 3 4 5 Good")
                alpha_words = sum(1 for w in words if re.search(r'[A-Za-z]{2,}', w)) # Words with at least 2 letters
                
                # Require majority of the block to be actual language, not just single characters/numbers
                if alpha_words >= 3 and (alpha_words / len(words)) >= 0.4:
                    valid_content_blocks.append(text_clean)
                    
        # Deduplicate blocks while preserving chronological reading order universally
        unique_blocks = []
        seen = set()
        for block in valid_content_blocks:
            if block not in seen:
                seen.add(block)
                unique_blocks.append(block)

        elapsed = round(time.time() - start_time, 2)
        logger(f"   -> [NLP Engine] Structural data perfectly extracted in {elapsed}s! Returning payload.")
        
        structured_response = [
            {
                "Status": "Advanced NLP Extraction Completed Successfully",
                "Execution_Time_Sec": elapsed,
                "Model_Used": "spaCy (en_core_web_sm) + Python re",
                "Results": {
                    "Top_Page_Topics": top_entities,
                    "Total_Valid_Sentences": len(unique_blocks),
                    "Clean_Extracted_Content": unique_blocks
                },
                "Source_Context_Sample": clean_text[:400] + "... [TRUNCATED FOR VIEW]"
            }
        ]
        
        return json.dumps(structured_response, indent=2)
        
    except Exception as e:
        logger(f"[NLP AI Error] Execution crashed: {e}")
        return json.dumps([{"Error": f"NLP Pipeline Crash: {str(e)}"}])

def execute_generative_fallback(prompt, structured_data_json, raw_text, logger=print):
    """V18 Stage 3: Generative LLM Context Fallback using Qwen or BGE dense chunking."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import json
    import time
    
    logger(f"\\n[Stage 3: Generative Context Engine] Processing intelligent query over scraped payloads natively...")
    start_time = time.time()
    
    try:
        # Load Model and Tokenizer dynamically into GPU VRAM
        model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        logger(f"   -> Instantiating {model_name} offline model weights. This is heavily VRAM bound...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16, 
            device_map="auto"
        )
        
        # 1. Semantic Embedding Routing (E5 / BGE-M3 Logic)
        logger("   -> [Semantic Router] Compressing context blocks using Vector Embeddings to prevent LLM hallucination...")
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        embedder = SentenceTransformer("BAAI/bge-large-en-v1.5", device=device)
        
        # Parse the structured JSON correctly instead of breaking it natively
        parsed_json = json.loads(structured_data_json)
        raw_blocks = []
        if isinstance(parsed_json, list) and len(parsed_json) > 0 and "Results" in parsed_json[0]:
            raw_blocks = parsed_json[0]["Results"].get("Clean_Extracted_Content", [])
            
        if not raw_blocks:
            # Fallback to chunking the raw text natively
            words = raw_text.split()
            raw_blocks = [" ".join(words[i:i + 50]) for i in range(0, len(words), 50)]
            
        # Execute Neural Similarity Search natively
        prompt_vec = embedder.encode([prompt])
        block_vecs = embedder.encode(raw_blocks)
        similarities = cosine_similarity(prompt_vec, block_vecs)[0]
        
        top_indices = np.argsort(similarities)[-15:][::-1] # Get Top 15 blocks
        top_indices.sort() # Preserve reading order
        
        clean_context = "\\n".join([f"- {raw_blocks[i]}" for i in top_indices])
        
        # Format explicitly via conversational Chat Template limits to prevent RAM explosions
        messages = [
            {"role": "system", "content": "You are a precise data extraction AI. You answer user queries accurately using the provided context. You must format your final output beautifully using standard Markdown styling (bolding, headers, bullet points). NEVER write JSON format in your response."},
            {"role": "user", "content": f"Context:\\n{clean_context}\\n\\nTask: {prompt}"}
        ]
        
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        
        logger("   -> Executing Causal Generation Sequence...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=400,
            temperature=0.3, # Low temp for data precision
            repetition_penalty=1.1
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Instant memory flush
        del model
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        elapsed = round(time.time() - start_time, 2)
        logger(f"   -> [Qwen Generator] Context explicitly resolved natively in {elapsed}s.")
        
        out = [{
            "Status": "Query Synthesized via Qwen2.5-1.5B-Instruct Fallback",
            "Execution_Time_Sec": elapsed,
            "User_Query": prompt,
            "Generated_Insight": response.strip()
        }]
        return json.dumps(out, indent=2)
        
    except Exception as e:
        logger(f"[Generative Engine Crash] Execution failed: {e}")
        return json.dumps([{"Error": f"Qwen Pipeline Crash: {str(e)}"}])

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
