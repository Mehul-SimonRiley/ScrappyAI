import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://modxcomputers.com/product-category/pc-components/graphics-card/"
print(f"--- ModX Computers Debugger ---")
print(f"Fetching: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, verify=False, timeout=10)
print(f"HTTP Status: {response.status_code}")

html = response.text
print(f"Total HTML length: {len(html)} characters")

rtx_count = html.title().count("RTX")
rx_count = html.title().count("RX ")
print(f"Occurrences of 'RTX' in source HTML: {rtx_count}")
print(f"Occurrences of 'RX ' in source HTML: {rx_count}")

soup = BeautifulSoup(html, 'html.parser')

print("\\n--- Extracting ALL links containing 'page' ---")
pages = set()
for a in soup.find_all('a', href=True):
    if 'page' in a['href']:
        pages.add(a['href'])
print(f"Found {len(pages)} pagination/page links: {list(pages)[:5]}")

print("\\n--- Attempting to extract all H2 and H3 names ---")
headers = soup.find_all(['h2', 'h3'])
print(f"Found {len(headers)} headers.")
for h in headers[:15]:
    text = h.text.strip()
    if text:
        print(f" - {text}")
