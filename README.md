# ScrappyAI - Next-Generation Cognitive Web Crawler

![ScrappyAI Header](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Playwright](https://img.shields.io/badge/Playwright-Enabled-green) ![Transformers](https://img.shields.io/badge/Transformers-CUDA-orange)

## 📌 Overview

**ScrappyAI** is an intelligent, completely offline, GPU-accelerated web scraping sandbox built for enterprise-grade data extraction. Unlike traditional HTML parsers that break when website structures change, ScrappyAI uses a tandem **Micro-AI Architecture**: 
1. **Dense Vector Mapping (`sentence-transformers`)** to dynamically "find" structural data containers on a page.
2. **Generative Text-to-Text (`flan-t5`)** natively formatting the ripped text blocks exclusively based on User Prompts—running directly on the host's CUDA hardware.

## 🚀 Key Features

*   **100% Local Inference Engine:** Completely eliminated deprecated HuggingFace HTTP APIs. The entire NLP cleansing loop runs offline on your GPU, securing absolute privacy and extreme speeds.
*   **Playwright Hybrid Ghost Spider:** Natively bypasses `Datadog`, `Cloudflare`, and advanced lazy-loading `IntersectionObservers` via simulated Smooth Mouse Wheel emulation and strict `networkidle` listeners.
*   **Target Authorization Modal:** Seamlessly prompts users with a beautifully styled UI modal to explicitly grant Chromium manual Bypass control if 403 Firewalls trap the background spider.
*   **Zero-Shot Structural Extractor:** You never write CSS classes! Simply type "Extract Phone Numbers and Names", and the native `BAAI/bge-large` encoder physically hunts the most statistically relevant semantic node on the page to rip data from!

## ⚙️ Architecture Pipeline

1.  **Pywebview Native GUI**: Launching `main.py` instantiates an incredibly lightweight Python webview serving identical modern dark-themed aesthetics without Electron bloat.
2.  **The Fetch/Render Phase**: A headless Chromium engine scrolls dynamically, halting after every Rotation to absolutely verify zero remaining XHR fetching APIs exist.
3.  **Semantic Chunking**: BeautifulSoup strips standard UI components (`script`, `nav`), building an array of valid Wrapper candidates natively.
4.  **Zero-Shot Scoring**: `SentenceTransformer` (on CUDA) computes Cosine Similarities against your exact Search Query to determine exactly which wrapper cluster represents the "Target Array".
5.  **GenAI Sanitization**: `flan-t5-base` intercepts the massive ripped wrapper block, reads your objective natively, and outputs only the strictly desired data formatting mathematically!

## 🛠️ Usage

1.  **Activate Environment:** Ensure you are in the `ienv` virtual environment natively.
2.  **Execute Pipeline:** `python main.py`
3.  **Prompt:** Enter URL `https://example.com` and specify explicit extraction targets `Restaurant Names` in the interface.
4.  **Bypass (If needed):** If the server deploys Cloudflare, click the `Deploy Native` button on the pop-up to take physical browser control natively.

## ⚠️ Anti-Bot Handling
If Cloudflare blocks background spider execution natively, a UI prompt (Dark Mode styled) intercepts the event allowing the developer to launch a visible Chromium instance directly. The Ghost Crawler will physically idle and wait for the developer to execute physical CAPTCHA bypasses before resuming mathematical DOM slicing!