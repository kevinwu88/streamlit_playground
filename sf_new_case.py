import streamlit as st
from simple_salesforce import Salesforce
import os

# Initialize Salesforce connection
sf = Salesforce(
    username = st.secrets["sf_username"],
    password = st.secrets["sf_password"],
    security_token = st.secrets["sf_security_token"],
    domain = st.secrets["sf_domain"]  # Use 'test' for sandbox
)

def create_case(subject, description, priority, origin):
    try:
        # Create a new case
        new_case = sf.Case.create({
            'Subject': subject,
            'Description': description,
            'Priority': priority,
            'Origin': origin
        })
        return new_case['id']
    except Exception as e:
        st.error(f"Error creating case: {str(e)}")
        return None

# Streamlit UI
st.title('Create Salesforce Case')

subject = st.text_input('Subject')
description = st.text_area('Description')
priority = st.selectbox('Priority', ['High', 'Medium', 'Low'])
origin = st.selectbox('Origin', ['Phone', 'Email', 'Web'])

if st.button('Create Case'):
    if subject and description:
        case_id = create_case(subject, description, priority, origin)
        if case_id:
            st.success(f"Case created successfully! Case ID: {case_id}")
    else:
        st.warning('Please fill out all required fields.')