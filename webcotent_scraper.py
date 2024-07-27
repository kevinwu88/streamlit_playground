import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import io
import zipfile

def extract_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()
        else:
            return f"Failed to retrieve content. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error occurred while processing {url}: {e}"

def create_download_zip(contents):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for url, content in contents.items():
            file_name = url.split('//')[1].replace('/', '_') + '.txt'
            zip_file.writestr(file_name, content)
    return zip_buffer.getvalue()

st.title('Web Content Extractor')

# Text area for URL input
urls_input = st.text_area("Enter URLs (one per line):", height=150)

if st.button('Extract Content'):
    if urls_input:
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        
        if urls:
            contents = {}
            progress_bar = st.progress(0)
            for i, url in enumerate(urls):
                content = extract_content(url)
                contents[url] = content
                progress_bar.progress((i + 1) / len(urls))
            
            st.success("Content extracted successfully!")
            
            # Create download button
            zip_file = create_download_zip(contents)
            st.download_button(
                label="Download Extracted Content",
                data=zip_file,
                file_name="extracted_contents.zip",
                mime="application/zip"
            )
        else:
            st.warning("Please enter at least one valid URL.")
    else:
        st.warning("Please enter some URLs.")