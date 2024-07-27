import streamlit as st
from simple_salesforce import Salesforce
import pandas as pd
import os


# Initialize Salesforce connection
sf = Salesforce(
    username = st.secrets["sf_username"],
    password = st.secrets["sf_password"],
    security_token = st.secrets["sf_security_token"],
    domain = st.secrets["sf_domain"]  # Use 'test' for sandbox
)

def get_latest_cases(limit=100):
    query = f"""
        SELECT Id, CaseNumber, Status, Priority
        FROM Case
        ORDER BY CreatedDate DESC
        LIMIT {limit}
    """
    
    result = sf.query(query)
    return result['records']

# Streamlit UI
st.title('Latest Salesforce Cases')

if st.button('Fetch Latest Cases'):
    with st.spinner('Fetching cases...'):
        cases = get_latest_cases()
        
        if cases:
            # Prepare data for DataFrame
            data = []
            for case in cases:
                case_link = f"https://{sf.sf_instance}/lightning/r/Case/{case['Id']}/view"
                data.append({
                    'Case Number': case['CaseNumber'],
                    'Status': case['Status'],
                    'Priority': case['Priority'],
                    'Link': f'<a href="{case_link}" target="_blank">View Case</a>'
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Display DataFrame with clickable links
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # Option to download as CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                csv,
                "case_data.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.warning('No cases found.')