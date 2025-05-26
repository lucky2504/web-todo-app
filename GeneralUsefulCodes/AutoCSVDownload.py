from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os


def setup_firefox_driver():
    firefox_options = Options()

    # Set download preferences
    download_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Downloads')
    os.makedirs(download_dir, exist_ok=True)

    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", download_dir)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                                   "application/vnd.ms-excel,application/excel,application/x-excel,application/x-msexcel")

    service = Service(r"C:\Users\laxminad\Documents\WebDriver\geckodriver.exe") # Update this path
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def download_data(url, driver):
    try:
        print(f"\nProcessing: {url}")
        driver.get(url)
        time.sleep(5)

        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='btn-text' and text()='Download Now']"))
        )
        parent_link = download_button.find_element(By.XPATH, "./..")

        print("Clicking download button...")
        driver.execute_script("arguments[0].click();", parent_link)

        time.sleep(10)
        return True

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False


def read_excel_file():
    try:
        # Get the path to the Desktop
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        excel_path = os.path.join(desktop_path, 'Stocks.xlsx')

        print(f"Reading Excel file from: {excel_path}")

        # Read the Excel file
        df = pd.read_excel(excel_path)

        # Print the column names for debugging
        print("Column names in Excel file:", df.columns.tolist())

        # Convert URLs to list, handling different possible column names
        if 'URL' in df.columns:
            urls = df['URL'].tolist()
        elif 'Url' in df.columns:
            urls = df['Url'].tolist()
        elif 'url' in df.columns:
            urls = df['url'].tolist()
        else:
            # If no URL column found, take the first column
            urls = df.iloc[:, 0].tolist()

        # Remove any NaN values and convert to strings
        urls = [str(url) for url in urls if pd.notna(url)]

        print(f"Found {len(urls)} URLs to process")
        return urls

    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return []


def main():
    try:
        # Read URLs from Excel
        urls = read_excel_file()

        if not urls:
            print("No URLs found in the Excel file.")
            return

        # Initialize driver
        driver = setup_firefox_driver()

        # Process each URL
        results = []
        for index, url in enumerate(urls, 1):
            print(f"\nProcessing URL {index}/{len(urls)}")
            success = download_data(url, driver)
            results.append({
                'URL': url,
                'Status': 'Success' if success else 'Failed'
            })

        # Save results
        results_df = pd.DataFrame(results)
        results_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Download_Results.xlsx')
        results_df.to_excel(results_path, index=False)
        print(f"\nResults saved to: {results_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
