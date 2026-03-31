import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_jd_digit(class_name):
    # Justdial uses CSS classes for digits in phone numbers (e.g., icon-dc might be 0, icon-fe might be 1).
    # This mapping changes occasionally. A common mapping mapping based on standard JD obfuscation:
    # We will extract the classes and map them. This is a best-effort mapping.
    # Often the classes end in strings that correspond to digits.
    # Ex: icon-acb=0, icon-yz=1, icon-wx=2, icon-vu=3, icon-ts=4, icon-rq=5, icon-po=6, icon-nm=7, icon-lk=8, icon-ji=9
    # We will try a few known mappings or just grab text if available.
    
    mapping = {
        "acb": "0", "yz": "1", "wx": "2", "vu": "3", "ts": "4",
        "rq": "5", "po": "6", "nm": "7", "lk": "8", "ji": "9",
        "dc": "+", "fe": "(", "hg": ")", "ba": "-"
    }
    
    for key, val in mapping.items():
        if key in class_name:
            return val
    return ""

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    # Uncomment next line to run headlessly if presentation doesn't require seeing it run, 
    # but seeing it run is usually better for presentation
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_justdial_hotels(target_results=100):
    output_file = "justdial_mumbai_hotels.xlsx"
    driver = setup_driver()
    url = "https://www.justdial.com/Mumbai/Hotels/nct-10255012"
    
    print(f"Loading '{url}'...")
    driver.get(url)
    
    # Wait for initial results
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.resultbox_info"))
        )
    except TimeoutException:
        print("Initial payload failed to load.")
        driver.quit()
        return

    records = []
    scraped_names = set()
    no_new_results_count = 0
    max_scroll_attempts_without_new = 5 # Reduced to prevent infinite loops
    
    print(f"Scrolling to load at least {target_results} hotels...")
    while len(records) < target_results and no_new_results_count < max_scroll_attempts_without_new:
        
        # Get current count
        current_boxes = driver.find_elements(By.CSS_SELECTOR, "div.resultbox_info")
        if not current_boxes:
            current_boxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'resultbox')]")
        initial_count = len(current_boxes)
        
        # Scroll to the last loaded element to trigger lazy loads safely on slow internet
        if current_boxes:
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", current_boxes[-1])
                time.sleep(1)
                driver.execute_script("window.scrollBy(0, 300);")
            except Exception:
                driver.execute_script("window.scrollBy(0, 1000);")
        else:
            driver.execute_script("window.scrollBy(0, 1000);")
            
        # Slow internet wait: give page more time to fetch data
        time.sleep(3)
        
        # Try to dismiss any popups blocking scroll
        try:
            webdriver.ActionChains(driver).send_keys("\x1b").perform() # ESC key
        except:
            pass
            
        # Try to click 'Load More' if it exists
        try:
            load_more = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'LOAD MORE', 'load more'), 'load more') or contains(translate(text(), 'VIEW ALL', 'view all'), 'view all')]")
            if load_more and load_more[-1].is_displayed():
                driver.execute_script("arguments[0].click();", load_more[-1])
                time.sleep(3)
        except Exception:
            pass
            
        # Wait up to 10 seconds for new elements to load if internet is slow
        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.resultbox_info")) > initial_count or \
                          len(d.find_elements(By.XPATH, "//div[contains(@class, 'resultbox')]")) > initial_count
            )
        except TimeoutException:
            pass # Just proceed and parse. No new items will increment the counter later.

        result_boxes = driver.find_elements(By.CSS_SELECTOR, "div.resultbox_info")
        if not result_boxes:
            result_boxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'resultbox')]")
            
        new_items_found = False
        
        for box in result_boxes:
            if len(records) >= target_results:
                break
                
            try:
                name_el = box.find_element(By.CSS_SELECTOR, ".resultbox_title_anchor")
                name = name_el.text.strip()
                
                if not name or name in scraped_names:
                    continue
                    
                new_items_found = True
                
                address = ""
                try:
                    addr_el = box.find_element(By.CSS_SELECTOR, ".resultbox_address")
                    address = addr_el.text.strip()
                except NoSuchElementException:
                    pass
                
                rating = "N/A"
                try:
                    rating_el = box.find_element(By.CSS_SELECTOR, ".resultbox_totalrate")
                    rating = rating_el.text.strip()
                except NoSuchElementException:
                    try:
                        rating_el = box.find_element(By.CSS_SELECTOR, ".green-box")
                        rating = rating_el.text.strip()
                    except NoSuchElementException:
                        pass
                
                contact = "N/A"
                try:
                    phone_els = box.find_elements(By.CSS_SELECTOR, ".callcontent")
                    if not phone_els:
                        phone_els = box.find_elements(By.XPATH, ".//*[contains(@class, 'contact')]")
                        
                    if phone_els:
                        contact_text = phone_els[0].text.strip()
                        if contact_text and any(c.isdigit() for c in contact_text):
                            contact = contact_text
                        else:
                            spans = phone_els[0].find_elements(By.CSS_SELECTOR, "span[class*='icon-']")
                            if spans:
                                digits = [get_jd_digit(span.get_attribute("class")) for span in spans]
                                decoded = "".join(digits)
                                if decoded: contact = decoded
                except Exception:
                    pass

                if contact == "N/A":
                    try:
                        tel_link = box.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
                        contact = tel_link.get_attribute("href").replace("tel:", "")
                    except NoSuchElementException:
                        pass

                records.append({
                    "Hotel Name": name,
                    "Address": address,
                    "Rating": rating,
                    "Contact Details": contact
                })
                scraped_names.add(name)
                
            except Exception as e:
                continue
                
        if new_items_found:
            no_new_results_count = 0
            print(f"Scraped {len(records)}/{target_results} hotels...")
        else:
            no_new_results_count += 1
            
    print(f"\nCompleted scraping. Total hotels fetched: {len(records)}")
    
    df = pd.DataFrame(records)
    df.to_excel(output_file, index=False)
    print(f"Successfully saved records to {output_file}")
    
    driver.quit()

if __name__ == "__main__":
    scrape_justdial_hotels(100)
