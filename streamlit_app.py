import streamlit as st

home_page = st.Page("home.py", title="Home", icon=":material/add_circle:")
sf_metascan = st.Page("sf_metascan.py", title="Metadata scan", icon=":material/add_circle:")
sf_case_page = st.Page("sf_case.py", title="Case search", icon=":material/add_circle:")
sf_new_case_page = st.Page("sf_new_case.py", title="Create a new case", icon=":material/add_circle:")
sf_view_case_page = st.Page("sf_view_case.py", title="View cases", icon=":material/add_circle:")
pdf_downloader_page = st.Page("pdf_downloader.py", title="Download PDF files", icon=":material/add_circle:")
webcotent_scraper_page = st.Page("webcotent_scraper.py", title="Download web content", icon=":material/add_circle:")

st.header("🚀 Kevin's Playground")
# st.logo('images/capicon.jpeg', icon_image='images/capicon.jpeg')
pg = st.navigation([home_page, sf_view_case_page, sf_case_page, sf_new_case_page, sf_metascan, webcotent_scraper_page, pdf_downloader_page])
pg.run()