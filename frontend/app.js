// DOM Elements
window.onerror = function(msg, url, line, col, error) {
    document.body.innerHTML += `<div style="position:fixed;top:10px;left:10px;background:red;color:white;padding:20px;z-index:9999;border-radius:10px;"><b>JS Crash:</b> ${msg}<br>Line: ${line}</div>`;
};

const body = document.body;
const themeToggleBtn = document.getElementById('theme-toggle');
const navHome = document.getElementById('nav-home');
const navResults = document.getElementById('nav-chat');
const viewDashboard = document.getElementById('view-dashboard');
const viewLoading = document.getElementById('view-loading');
const viewResults = document.getElementById('view-results');
const pageTitle = document.getElementById('page-title');

const urlInput = document.getElementById('url-input');
const promptInput = document.getElementById('prompt-input');
const startBtn = document.getElementById('start-btn');
const errorBanner = document.getElementById('error-banner');
const errorText = document.getElementById('error-text');

const resultsBox = document.getElementById('results-box');
const newScrapeBtn = document.getElementById('new-scrape-btn');

// --- Anti-Bot Modal Elements ---
const authModal = document.getElementById('auth-modal');
const modalCancelBtn = document.getElementById('modal-cancel-btn');
const modalConfirmBtn = document.getElementById('modal-confirm-btn');

// --- Navigation & Theming ---
function switchView(viewId, title) {
    // Hide all views with fade out
    [viewDashboard, viewLoading, viewResults].forEach(v => {
        v.classList.remove('active-view');
        setTimeout(() => { if(!v.classList.contains('active-view')) v.classList.add('hidden'); }, 300);
    });
    
    // Manage Nav active states
    navHome.classList.remove('active');
    navResults.classList.remove('active');
    if (viewId === 'view-dashboard') navHome.classList.add('active');
    if (viewId === 'view-results') navResults.classList.add('active');

    // Show target view with fade in
    const target = document.getElementById(viewId);
    target.classList.remove('hidden');
    // tiny delay to allow display styles to apply before opacity transition fires
    setTimeout(() => target.classList.add('active-view'), 10);
    
    pageTitle.textContent = title || 'Web Crawler & Scraper Sandbox';
}

navHome.addEventListener('click', () => switchView('view-dashboard', 'Web Crawler & Scraper Sandbox'));
navResults.addEventListener('click', () => switchView('view-results', 'Target Extracted Data'));
newScrapeBtn.addEventListener('click', () => switchView('view-dashboard', 'Web Crawler & Scraper Sandbox'));

themeToggleBtn.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    const isDark = body.classList.contains('dark-theme');
    
    // Update button icon
    themeToggleBtn.innerHTML = isDark 
        ? '<i class="ph ph-sun"></i> Light Mode' 
        : '<i class="ph ph-moon"></i> Dark Mode';
        
    // Tell Python backend the theme changed (optional but good for syncing bounds)
    if (window.pywebview) {
        window.pywebview.api.log(`Theme toggled to ${isDark ? 'Dark' : 'Light'}`);
    }
});

// --- Validation & Error Banner ---
function showError(msg) {
    errorText.textContent = msg;
    errorBanner.classList.remove('hidden');
    // Re-trigger shake animation
    errorBanner.style.animation = 'none';
    errorBanner.offsetHeight; /* trigger reflow */
    errorBanner.style.animation = null; 
}

function hideError() {
    errorBanner.classList.add('hidden');
}

// --- Asynchronous Modal Interceptors (Called explicitly by Python) ---
window.showAuthModal = function() {
    authModal.classList.remove('hidden');
};

modalCancelBtn.addEventListener('click', () => {
    authModal.classList.add('hidden');
    if (window.pywebview) window.pywebview.api.respond_auth(false);
});

modalConfirmBtn.addEventListener('click', () => {
    authModal.classList.add('hidden');
    if (window.pywebview) window.pywebview.api.respond_auth(true);
});

// --- Interaction with Python Backend (PyWebView) ---

// --- Interaction with Python Backend (PyWebView) ---

// Stage 1: Browser Launch and Data Scrape
startBtn.addEventListener('click', async () => {
    hideError();
    const url = urlInput.value.trim();

    if (!url) {
        showError("Target URL cannot be empty.");
        return;
    }

    // Switch to Loading View
    switchView('view-loading', 'Active Task: Target Browser Scrape');
    
    try {
        // CALL PYTHON BACKEND EXPOSED STAGE 1 API
        const result = await window.pywebview.api.start_scraping(url);
        
        if (result.success) {
            // Move to clean results viewer where the user can now prompt the AI
            switchView('view-results', 'Stage 2: Target Extracted Data');
            resultsBox.innerText = result.answer; 
        } else {
            // Backend failed (fake URL, 404, bot block, etc)
            switchView('view-dashboard', 'Launch Chromium Native Engine');
            showError(result.error);
        }
    } catch (e) {
        switchView('view-dashboard', 'Launch Chromium Native Engine');
        showError("Failed to communicate with PyWebView Stage 1 Backend.");
    }
});

// Stage 2: Offline Generative AI Target Extraction
document.getElementById('extract-ai-btn').addEventListener('click', async () => {
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        resultsBox.innerText = "Please specify what exactly to extract from the scraped data...\\n\\nExample: 'Extract all restaurants and phone numbers.'";
        return;
    }
    
    resultsBox.innerText = "🧠 Initializing Local Generative AI Tensor inference natively...\\nSearching cached raw data...";
    document.getElementById('extract-ai-btn').innerHTML = '<i class="ph ph-spinner"></i>';
    
    try {
        // Calling Stage 2 Endpoint locally WITHOUT triggering network scraping
        const jsonStr = await window.pywebview.api.execute_ai_query(prompt);
        
        try {
            const data = JSON.parse(jsonStr);
            if (data[0] && data[0].Response) {
                resultsBox.innerText = data[0].Response;
            } else if (data[0] && data[0].Error) {
                resultsBox.innerText = "Execution Fault: " + data[0].Error;
            } else {
                resultsBox.innerText = JSON.stringify(data, null, 2);
            }
        } catch(parseErr) {
            resultsBox.innerText = jsonStr; // Direct fallback
        }
    } catch (e) {
        resultsBox.innerText = "Failed to communicate with PyWebView AI Tensors.";
    }
    
    document.getElementById('extract-ai-btn').innerHTML = 'Extract <i class="ph ph-magic-wand"></i>';
});

