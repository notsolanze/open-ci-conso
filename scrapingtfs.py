import streamlit as st
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'previous_data' not in st.session_state:
    st.session_state.previous_data = pd.DataFrame()
    st.session_state.new_indices = []

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def play_notification_sound():
    audio_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def highlight_new_rows(row):
    if row.name in st.session_state.new_indices:
        return ['background-color: #90EE90'] * len(row)
    return [''] * len(row)

def scrape_website(url):
    driver = None
    try:
        driver = setup_selenium()
        if not driver:
            st.error("Failed to initialize web driver")
            return None

        logger.info(f"Scraping URL: {url}")
        driver.get(url)
        
        # Wait for the table to be present
        wait = WebDriverWait(driver, 30)
        table = wait.until(EC.presence_of_element_located((By.ID, 'todoListTable')))
        
        # Get the page source after JavaScript rendering
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        
        # Find the table in the page
        table = soup.find('table', {'id': 'todoListTable'})
        if not table:
            logger.warning("No table found on the page")
            return None

        # Extract table headers
        headers = [th.text.strip() for th in table.find_all('th')]

        # Extract table rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            row = [td.text.strip() for td in tr.find_all('td')]
            if row:  # Only add non-empty rows
                rows.append(row)

        # Create DataFrame
        if headers and rows:
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"Successfully scraped {len(df)} rows")
        else:
            logger.warning("No data found in the table")
            return None
        
        return df

    except TimeoutException:
        logger.error("Timeout waiting for table to load")
        st.error("Timeout waiting for table to load. The website might be slow or unavailable.")
        return None
    except NoSuchElementException:
        logger.error("Table element not found on the page")
        st.error("The expected table was not found on the page. The website structure might have changed.")
        return None
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        st.error(f"An error occurred while scraping: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    st.title("Real-Time Auto Dealer Application Monitor")
    
    url = st.text_input("Enter the URL to monitor:", "https://los.toyotafinancial.ph/clos/TodoList.do")
    
    st.write(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    interval = st.slider("Refresh interval (seconds)", min_value=30, max_value=300, value=60)
    
    if st.button("Scrape Data"):
        current_data = scrape_website(url)
        
        if current_data is not None:
            if not st.session_state.previous_data.empty:
                new_records = current_data[~current_data.iloc[:, 1].isin(
                    st.session_state.previous_data.iloc[:, 1]
                )]
                
                if not new_records.empty:
                    st.session_state.new_indices = new_records.index
                    play_notification_sound()
                    st.success(f"Found {len(new_records)} new entries!")
                else:
                    st.session_state.new_indices = []
            else:
                st.session_state.new_indices = []
            
            st.dataframe(
                current_data.style.apply(highlight_new_rows, axis=1),
                height=400
            )
            
            st.session_state.previous_data = current_data
            
            filter_text = st.text_input("Filter records:")
            if filter_text:
                filtered_df = current_data[
                    current_data.astype(str).apply(
                        lambda x: x.str.contains(filter_text, case=False)
                    ).any(axis=1)
                ]
                st.dataframe(
                    filtered_df.style.apply(highlight_new_rows, axis=1),
                    height=400
                )
        
            csv = current_data.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"dealer_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()

