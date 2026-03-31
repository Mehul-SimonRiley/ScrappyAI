# ScrappyAI: The Offline Multi-Model Intelligent Scraper
An industrial-grade, locally hosted Web Crawler & Advanced NLP Extraction Pipeline built natively in Python.

## Core Architecture
ScrappyAI strictly avoids the fragile "blindly feed the LLM" approach. It utilizes a highly deterministic, multi-staged routing sequence to guarantee JSON outputs are completely free of hallucination:
1. **Physical Chromium Crawler (`Playwright`)**: Ultra-conservative `200px` micro-scrolling permanently renders all delayed React/Vue DOM elements automatically.
2. **Structural Cleaning Engine (`BeautifulSoup`)**: Completely rips out scripts, styles, and stop-word noise while mathematically collapsing whitespaces (`\n`).
3. **Advanced Fast-Mapping (`spaCy + Regex`)**: Employs `en_core_web_sm` to natively extract Orgs, People, and Products, eliminating UI artifacts globally via Alphanumeric density verification without pinging an LLM.
4. **Retrieval-Augmented Generative Fallback (`Qwen-1.5B` & `BAAI/bge-large`)**: If the user submits an analytical query, the local Vector Engine slices the structured data and routes only the Top 15 semantic matches directly to Qwen. This generates ChatGPT-style Markdown insights securely with $<3.5$ GB of VRAM.

## Requirements
* Python 3.10+
* 6GB GPU VRAM (for Qwen-1.5B-Instruct Offline generation capability)
* Internet Connection (for the Chromium spider phase)

## Deployment Options

### 1. Developer Setup
Clone the repository and install dependencies cleanly into a Virtual Environment:
```powershell
python -m venv ienv
.\ienv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
playwright install chromium
```

Run the GUI seamlessly:
```powershell
python main.py
```

### 2. Standalone Downloadable `.exe` Release
If you download the standalone `ScrappyAI.exe` from the Releases tab:
* No Python installation is required to launch the GUI.
* **NOTE:** Since the software requires the `playwright` framework, it may prompt you to install chromium bounds if your Windows environment hasn't physically seen an isolated instance before.
* HuggingFace Models (`BGE-M3` & `Qwen`) will automatically download weights globally to your `~/.cache/huggingface` upon initial operation to save file space.

**Created natively as an Internship Web Extraction Prototype.**