import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import io
import zipfile

def find_pdf_links(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            pdf_links = []
            for link in links:
                href = link['href']
                if href.lower().endswith('.pdf'):
                    pdf_url = urllib.parse.urljoin(url, href)
                    pdf_links.append(pdf_url)
            return pdf_links
        else:
            st.error(f"Failed to retrieve content. Status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        st.error(f"Error occurred while processing {url}: {e}")
        return []

def download_pdf(pdf_url):
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            return response.content
        else:
            st.warning(f"Failed to download: {pdf_url}")
            return None
    except requests.RequestException as e:
        st.warning(f"Error downloading {pdf_url}: {e}")
        return None

st.title('PDF Downloader from Webpage')

# Initialize session state
if 'pdf_links' not in st.session_state:
    st.session_state.pdf_links = []
if 'selected_pdfs' not in st.session_state:
    st.session_state.selected_pdfs = set()

url = st.text_input("Enter the URL of the webpage containing PDF links:")

if st.button('Find PDF Links'):
    if url:
        with st.spinner('Searching for PDF links...'):
            st.session_state.pdf_links = find_pdf_links(url)
        
        if st.session_state.pdf_links:
            st.success(f"Found {len(st.session_state.pdf_links)} PDF links!")
        else:
            st.warning("No PDF links found on the given webpage.")
    else:
        st.warning("Please enter a URL.")

# Display checkboxes for each PDF
if st.session_state.pdf_links:
    st.write("Select PDFs to download:")
    for pdf_url in st.session_state.pdf_links:
        if st.checkbox(f"Select {pdf_url.split('/')[-1]}", key=pdf_url, value=pdf_url in st.session_state.selected_pdfs):
            st.session_state.selected_pdfs.add(pdf_url)
        else:
            st.session_state.selected_pdfs.discard(pdf_url)

# Download button
if st.session_state.selected_pdfs:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for pdf_url in st.session_state.selected_pdfs:
            pdf_content = download_pdf(pdf_url)
            if pdf_content:
                zip_file.writestr(pdf_url.split('/')[-1], pdf_content)
    
    zip_buffer.seek(0)

    st.download_button(
        label="Download ",
        data=zip_buffer.getvalue(),
        file_name="downloaded_pdfs.zip",
        mime="application/zip",
        key="download_button"
    )
    # st.success("PDFs downloaded successfully!")
    # if st.button('Download Selected PDFs'):
    #     with st.spinner('Downloading PDFs...'):
    #         zip_buffer = io.BytesIO()
    #         with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
    #             for pdf_url in st.session_state.selected_pdfs:
    #                 pdf_content = download_pdf(pdf_url)
    #                 if pdf_content:
    #                     zip_file.writestr(pdf_url.split('/')[-1], pdf_content)
            
    #         zip_buffer.seek(0)
            
    #         # Trigger the download
    #         st.download_button(
    #             label="Click here if download doesn't start automatically",
    #             data=zip_buffer.getvalue(),
    #             file_name="downloaded_pdfs.zip",
    #             mime="application/zip",
    #             key="download_button"
    #         )
            
    #         # Automatically trigger the download
    #         st.markdown(
    #             f"""
    #             <script>
    #                 document.querySelector('button[key="download_button"]').click();
    #             </script>
    #             """,
    #             unsafe_allow_html=True
    #         )
        
        # st.success("PDFs downloaded successfully!")

# Display selected PDFs
# if st.session_state.selected_pdfs:
#     st.write("Selected PDFs:")
#     for pdf_url in st.session_state.selected_pdfs:
#         st.write(f"- {pdf_url.split('/')[-1]}")