import os
import time
import logging
from typing import List, Dict, Any
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

# Configuration from environment variables
WAIT_TIMEOUT = int(os.getenv('SCRAPER_WAIT_TIMEOUT', '30'))
DYNAMIC_WAIT = int(os.getenv('SCRAPER_DYNAMIC_WAIT', '5'))

def scrape_dynamic_products(url: str) -> List[Dict[str, Any]]:
    """
    Scrapes products from a dynamic website, waiting for late-loaded content.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless=new') # type: ignore
    chrome_options.add_argument('--no-sandbox') # type: ignore
    chrome_options.add_argument('--disable-dev-shm-usage') # type: ignore
    chrome_options.add_argument('--disable-gpu') # type: ignore
    chrome_options.add_argument('--window-size=1920,1080') # type: ignore
    chrome_options.add_argument('--start-maximized') # type: ignore
    chrome_options.add_argument('--disable-extensions') # type: ignore
    chrome_options.binary_location = os.getenv('CHROME_BIN', '/usr/bin/chromium')
    
    service = webdriver.ChromeService(
        executable_path=os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    )
    
    products = []
    logger.info(f"Starting scraper for URL: {url}")
    
    driver = None
    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            logger.info("Chrome driver initialized")
            driver.get(url)
            logger.info("Page loaded")
            
            # Wait for document ready state
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: d.execute_script('return document.readyState') == 'complete' # type: ignore
            )
            logger.info("Page load complete")
            
            # Log current state
            logger.info(f"Current URL: {driver.current_url}")
            logger.debug(f"Initial page source:\n{driver.page_source}")
            
            # Wait for status element
            status = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "status"))
            )
            logger.info(f"Found status element: {status.text}")
            
            # Wait for "Done" status
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.text_to_be_present_in_element((By.ID, "status"), "Done")
            )
            logger.info("Status changed to 'Done'")
            
            # Find product elements
            product_elements = driver.find_elements(By.TAG_NAME, "li")
            
            if not product_elements:
                logger.warning("No product elements found")
                logger.debug(f"Final page source:\n{driver.page_source}")
                return []
            
            logger.info(f"Found {len(product_elements)} product elements")
            
            # Parse products
            for element in product_elements:
                try:
                    text_parts = element.text.split(' | ')
                    if len(text_parts) != 4:
                        logger.warning(f"Skipping malformed product text: {element.text}")
                        continue
                    
                    product = { # type: ignore
                        'product_id': text_parts[0],
                        'name': text_parts[1],
                        'category': text_parts[2],
                        'price': float(text_parts[3].replace('$', '')),
                        'currency': 'USD',
                        'rating': 0.0,
                        'in_stock': True,
                        'last_updated': datetime.now().isoformat(),
                        'source': 'scrape',
                        'ingested_at': datetime.now().isoformat()
                    }
                    products.append(product) # type: ignore
                except (IndexError, ValueError) as e:
                    logger.error(f"Failed to parse product: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(products)} products")
            return products
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        if driver is not None:
            logger.debug(f"Final page source:\n{driver.page_source}")
        raise
        raise
