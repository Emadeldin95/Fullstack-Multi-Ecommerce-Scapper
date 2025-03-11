import asyncio
from playwright.async_api import async_playwright
import pandas as pd

class Scraper:
    def __init__(self, url, keywords=None):
        self.url = url
        self.keywords = keywords
        self.data = []
        self.running = True

    async def start_scraping(self, update_callback):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(self.url)

            # **Identify the Correct Search Input**
            search_selectors = [
                'input.wp-block-search__input',  # Electra Store
                'input[name="s"][type="search"]',  # General WooCommerce search
                'input.dgwt-wcas-search-input'  # WooCommerce AJAX search
            ]
            search_box = None

            # **Find a Search Input That Exists**
            for selector in search_selectors:
                try:
                    await page.wait_for_selector(selector, state="visible", timeout=5000)
                    search_box = await page.query_selector(selector)
                    if search_box:
                        break  # Found a valid search input
                except:
                    continue  # Try next selector if this one fails

            if search_box and self.keywords:
                # **Ensure the search box is enabled before filling**
                await page.evaluate('(el) => el.removeAttribute("disabled")', search_box)

                # **Fill the search box with the keyword**
                await search_box.fill(self.keywords)

                # **Trigger an input event to ensure the website detects the change**
                await page.evaluate('(el) => el.dispatchEvent(new Event("input", { bubbles: true }))', search_box)

                # **Try Clicking the Search Button (if available)**
                search_button = await page.query_selector('button.wp-block-search__button') or \
                                await page.query_selector('button[type="submit"]')

                if search_button:
                    await search_button.click()
                else:
                    await search_box.press("Enter")  # Press Enter if no button exists

                await page.wait_for_load_state("networkidle")  # Wait for results to load

            # **Dynamic Product Selectors**
            product_selectors = [
                '.product-wrapper',  # Makerselectronics
                'li.entry.has-media',  # Electra Store
                '.product'  # Generic WooCommerce
            ]

            # **Pagination Selector**
            next_page_selector = 'a.next.page-numbers'

            # **Scraping Loop**
            while self.running:
                product_container = None
                for selector in product_selectors:
                    product_container = await page.query_selector_all(selector)
                    if product_container:
                        break  # Found a valid product structure

                if not product_container:
                    print("⚠ No products found on this page.")
                    break

                for product in product_container:
                    if not self.running:
                        break

                    # **Extract Product Name**
                    name_element = await product.query_selector('h3.heading-title.product-name a') or \
                                   await product.query_selector('h2 a')
                    name = await name_element.inner_text() if name_element else "N/A"

                    # **Extract Price**
                    price_element = await product.query_selector('.price bdi') or \
                                    await product.query_selector('.woocommerce-Price-amount.amount')
                    price = await price_element.inner_text() if price_element else "N/A"

                    # **Extract Product Link**
                    link_element = await product.query_selector('h3.heading-title.product-name a') or \
                                   await product.query_selector('h2 a')
                    link = await link_element.get_attribute("href") if link_element else "N/A"

                    # **Append Data and Update UI**
                    self.data.append({"Name": name, "Price": price, "Link": link})
                    update_callback(self.data)

                # **Pagination Handling**
                next_page_button = await page.query_selector(next_page_selector)
                if next_page_button:
                    next_page_url = await next_page_button.get_attribute("href")
                    await page.goto(next_page_url)  # Move to next page
                    await page.wait_for_load_state("networkidle")
                else:
                    break  # Stop if no more pages

            await browser.close()

    def stop(self):
        self.running = False

    def get_data(self):
        return pd.DataFrame(self.data)
