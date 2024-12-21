import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Specify the path to your chromedriver
chrome_driver_path = r"D:\downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Set up Chrome options
options = Options()
options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
# options.add_argument("--headless")  # Uncomment this to run in headless mode
options.add_argument("--no-sandbox")  # Prevent sandboxing (optional)
options.add_argument("--enable-logging")  # Enable detailed logs
options.add_argument("--v=1")  # Verbose logging for ChromeDriver

# Start the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# The URLs to extract data from
urls = [
    "https://www.nhsinform.scot/illnesses-and-conditions/cardiovascular-disease/heart-disease/heart-attack/",
    "https://www.nhsinform.scot/illnesses-and-conditions/diabetes/diabetes/",
    "https://www.nhsinform.scot/illnesses-and-conditions/brain-nerves-and-spinal-cord/migraine/",
    "https://www.nhsinform.scot/illnesses-and-conditions/kidneys-bladder-and-prostate/kidney-infection/"
]

# Initialize a list to store data for all pages
all_data = []

for url in urls:
    # Open the webpage
    driver.get(url)

    # Wait for the page to load completely
    time.sleep(3)

    # Initialize a dictionary to store extracted data for the current page
    page_data = {"URL": url}

    try:
        # Extract the content of h1 (page title)
        h1_element = driver.find_element(By.TAG_NAME, 'h1')
        h1_text = h1_element.text if h1_element else 'N/A'
        page_data['H1'] = h1_text

        # Extract content from each h2 tag and its associated content
        h2_elements = driver.find_elements(By.TAG_NAME, 'h2')

        for h2 in h2_elements:
            h2_text = h2.text.strip()
            if h2_text:
                # Initialize a list to collect the content (p or li elements) under each h2
                content_text = []

                # Find all sibling elements following the h2 tag
                sibling_elements = h2.find_elements(By.XPATH, "following-sibling::*")

                for element in sibling_elements:
                    # Check if the sibling is a p or li element, or a parent containing li
                    if element.tag_name == 'p':
                        content_text.append(element.text.strip())
                    elif element.tag_name == 'ul' or element.tag_name == 'ol':
                        # If it's a list, collect all li tags inside the list
                        li_elements = element.find_elements(By.TAG_NAME, 'li')
                        for li in li_elements:
                            content_text.append(li.text.strip())
                    elif element.tag_name == 'li':
                        # If it's a direct li element, add it directly to the list
                        content_text.append(element.text.strip())
                    else:
                        # Stop processing if a non-p, non-li, non-list tag is encountered
                        break

                # Store the content under the respective h2 header if there is any content
                if content_text:
                    page_data[h2_text] = content_text

    except Exception as e:
        print(f"Error processing {url}: {e}")

    # Add the page data to the list of all data
    all_data.append(page_data)

# Write the collected data to a JSON file
with open("chronic_disease_data.json", "w", encoding='utf-8') as jsonfile:
    json.dump(all_data, jsonfile, ensure_ascii=False, indent=4)

# Close the browser after finishing
driver.quit()
