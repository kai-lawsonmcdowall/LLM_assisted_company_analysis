from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, TimeoutException
import time
import re
import pandas as pd


def parse_released_time(released):
    if not isinstance(released, str):
        return (float("inf"), float("inf"))
    match = re.match(r"(\d+) (seconds?|minutes?|hours?) ago", released)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        # Map both singular and plural forms of time units
        order = {
            "second": 1,
            "seconds": 1,
            "minute": 2,
            "minutes": 2,
            "hour": 3,
            "hours": 3,
        }
        return (order[unit], value)
    return (float("inf"), float("inf"))


def scrape_search_element(search_element, company_name):
    try:
        title_h3 = search_element.find_element(By.CSS_SELECTOR, "h3")
        title = title_h3.get_attribute("innerText")
    except NoSuchElementException:
        title = None

    try:
        url_a = search_element.find_element(By.CSS_SELECTOR, "a:has(> h3)")
        url = url_a.get_attribute("href")
    except NoSuchElementException:
        url = None

    try:
        description_div = search_element.find_element(
            By.CSS_SELECTOR, "[data-sncf='1']"
        )
        description = description_div.get_attribute("innerText")
    except NoSuchElementException:
        description = None

    released_match = re.search(
        r"\d+ (?:seconds?|minutes?|hours?) ago", description or ""
    )
    released = released_match.group(0) if released_match else None

    if released:
        released = re.sub(
            r"\b(hour|minute|second)\b", lambda m: m.group(1) + "s", released
        )

    return {
        "released": released,
        "title": title,
        "url": url,
        "description": description,
        "company": company_name,
    }


def initialize_driver():
    """Initialize the Chrome WebDriver."""

    options = Options()

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )  # potential helps captcha avoidance
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])  # potential helps captcha avoidance
    # options.add_experimental_option("useAutomationExtension", False)  ##potential helps captcha avoidance

    # options.add_argument("--headless")  # Uncomment this for headless mode in production

    return webdriver.Chrome(service=Service(), options=options)


def accept_cookies(driver):
    """Accept cookies if prompted."""
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "[role='dialog'] button")
        accept_all_button = next(
            (b for b in buttons if "Accept all" in b.get_attribute("innerText")), None
        )
        if accept_all_button:  # Check if button exists before clicking
            accept_all_button.click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Accept all']"))
        ).click()
    except TimeoutException:
        pass  # No cookies dialog appeared, so we continue normally


def perform_google_search(driver, term):
    """Perform Google search for the given term."""
    search_box = driver.find_element(By.CSS_SELECTOR, "textarea[aria-label='Search']")
    search_box.send_keys(f"{term} news")
    search_box.submit()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search"))
    )


def click_element_with_retries(driver, by, value, retries=3):
    """Click an element with retry logic."""
    for _ in range(retries):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, value))
            ).click()
            return True
        except TimeoutException:
            time.sleep(3)
    return False


def filter_past_24_hours(driver):
    """Apply past 24 hours filter to Google search results."""
    if click_element_with_retries(driver, By.ID, "hdtb-tls"):
        click_element_with_retries(driver, By.XPATH, "//div[text()='Any time']")
        click_element_with_retries(driver, By.XPATH, "//a[text()='Past 24 hours']")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#search"))
        )


def scrape_search_results(driver, term):
    """Scrape search results and return a list of dictionaries."""
    elements = driver.find_elements(
        By.CSS_SELECTOR, "div[jscontroller][lang][jsaction][data-hveid][data-ved]"
    )
    results = [scrape_search_element(e, term) for e in elements]
    try:
        first_element = driver.find_element(By.CSS_SELECTOR, "div.g[data-hveid]")
        results.insert(0, scrape_search_element(first_element, term))
    except NoSuchElementException:
        pass
    return pd.DataFrame(results).drop_duplicates().to_dict("records")


def search_with_retries(terms, all_results, failed_terms, retries=3):
    """
    Perform Google searches and retry failed ones up to a specified number of attempts.

    Args:
        terms (list): List of search terms.
        all_results (list): List to store successfully scraped results.
        failed_terms (list): Predefined empty list to store failed search terms.
        retries (int, optional): Number of retry attempts per term. Defaults to 3.
    """
    # Initial search attempt for all terms
    for term in terms:
        try:
            with initialize_driver() as driver:
                driver.get("https://www.google.com/?hl=en-US")
                accept_cookies(driver)
                perform_google_search(driver, term)
                filter_past_24_hours(driver)
                all_results.extend(scrape_search_results(driver, term))
        except Exception as e:
            print(f"Error processing {term}: {e}")
            failed_terms.append(term)

    # Retry failed searches
    for attempt in range(1, retries + 1):
        if not failed_terms:
            break  # Exit if no failed terms remain

        print(f"Retry attempt {attempt} for failed searches...")
        remaining_failed_terms = failed_terms[:]
        failed_terms.clear()

        for term in remaining_failed_terms:
            try:
                with initialize_driver() as driver:
                    driver.get("https://www.google.com/?hl=en-US")
                    accept_cookies(driver)
                    perform_google_search(driver, term)
                    filter_past_24_hours(driver)
                    all_results.extend(scrape_search_results(driver, term))
            except Exception as e:
                print(f"Retry failed for {term}: {e}")
                failed_terms.append(term)

            time.sleep(5)  # Wait before the next retry
