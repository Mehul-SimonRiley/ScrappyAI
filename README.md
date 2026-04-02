# 🦅 ScrappyAI - Enterprise Desktop Interface

![Scrappy AI Banner](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python) ![AI Engine](https://img.shields.io/badge/AI_Engine-Qwen_1.5B-orange?style=for-the-badge)

**ScrappyAI** is an advanced, fully autonomous offline Web Scraping and Machine Learning intelligence suite. Built entirely with local inferencing bounds, it combines the structural parsing power of `Playwright` and `spaCy` with the deep generative semantic vector networking of `BGE-M3` and `Qwen-1.5B-Instruct`.

---

## 🚀 Key Features
- **100% Offline AI Execution:** The entire generative fallback architecture runs strictly isolated on your local processor. No paid API keys. No data leaks.
- **Micro-Executable Deployment (~280 MB):** ScrappyAI features a highly advanced auto-downloader. First-time users simply launch the lightweight application, and the structural neural networks (4.5GB) will install themselves directly alongside the executable autonomously!
- **Infinite Scroll Engine:** Bypasses conventional crawler restrictions natively by hijacking raw Chromium window contexts to defeat Imperva, Cloudflare, and advanced captchas naturally.
- **PyWebView UI Integration:** Seamless HTML5 GUI wrapper communicating instantly over Python WebSockets to process neural payloads.

---

## 📥 Download the Standalone App
You do not need to install Python to use ScrappyAI natively! 
1. **[Download Part 1 Here](https://github.com/Mehul-SimonRiley/ScrappyAI/releases/download/v1.0.0/ScrappyAI_Release.part1.rar)** and **[Download Part 2 Here](https://github.com/Mehul-SimonRiley/ScrappyAI/releases/download/v1.0.0/ScrappyAI_Release.part2.rar)** 
2. Due to the massive GPU Neural acceleration dependencies (PyTorch / CUDA), the application is distributed as a multi-part archive. Place **both** `.rar` files (`part1` and `part2`) firmly on your Desktop or in the same folder.
3. Right-click **strictly** on `ScrappyAI_V1.part1.rar` and select "Extract Here". WinRAR will automatically stitch both files together seamlessly!
4. Open the extracted folder and double-click `ScrappyAI_V1.exe`.
5. *On your very first execution, the system will prompt you for authorization to securely download the required 4.5 GB Artificial Intelligence weights. A temporary console will unhide to show exactly what is downloading. Once complete, it's yours forever!*

---

## 🛠️ Developer Installation Requirements (Source Code)
If you wish to compile the application yourself or edit the neural pathways, your system must meet specific dependencies:

### 1. Prerequisites
- **Python 3.10+**
- Visual Studio C++ Build Tools (Required for `huggingface_hub` deep compiling)
- At least **6 GB of unused RAM / VRAM** mathematically to run Qwen locally.

### 2. Environment Setup
Clone the repository and install all strict Python dependencies natively:
```powershell
# Clone the system
git clone https://github.com/Mehul-SimonRiley/ScrappyAI.git
cd ScrappyAI/Scrappy_AI

# Instantiate Virtual Bounds natively
python -m venv ienv
ienv\Scripts\activate

# Install the Python matrices
pip install -r requirements.txt
```

### 3. Execution
Launch the Python application manually:
```powershell
python main.py
```
> The architecture will inherently detect if your `offline_models` are missing and mathematically instantiate the Neural Downloading Sequence dynamically!

---

## 🏗️ Deep Compilation (Building the .exe)
To package the executable exactly as deployed in production, `Pyinstaller` is utilized to map the HTML assets into the internal Temp paths (`sys._MEIPASS`).

```powershell
python -m PyInstaller -y --onedir --add-data "frontend;frontend" main.py --name "ScrappyAI_V1"
```
The final lightweight application will populate in the `dist/ScrappyAI_V1` directory, totally ready for compression and distribution via ZIP!

---
*Created and Engineered natively using cutting edge Generative Context Frameworks.*