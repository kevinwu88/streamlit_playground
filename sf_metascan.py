import streamlit as st
from simple_salesforce import Salesforce, SFType
import json
from openai import OpenAI
import requests

# Salesforce credentials
SF_USERNAME = "your_salesforce_username"
SF_PASSWORD = "your_salesforce_password"
SF_SECURITY_TOKEN = "your_salesforce_security_token"

# OpenAI API key
OPENAI_API_KEY = st.secrets["openai_api_key"]

def connect_to_salesforce():
    try:
        sf = Salesforce(
            username = st.secrets["sf_username"],
            password = st.secrets["sf_password"],
            security_token = st.secrets["sf_security_token"],
            domain = st.secrets["sf_domain"]  # Use 'test' for sandbox
        )
        return sf
    except Exception as e:
        st.error(f"Failed to connect to Salesforce: {str(e)}")
        return None

def fetch_metadata(sf, metadata_type):
    try:
        sf_instance_url = 'https://canbsdo.my.salesforce.com'
        metadata_url = f'{sf_instance_url}/services/data/v52.0/tooling/query/?q=SELECT+Id,+Metadata+FROM+SecuritySettings'

        response = requests.get(
            metadata_url,
            headers={'Authorization': f'Bearer {sf.session_id}'}
        )

        if response.status_code == 200:
            security_settings = response.json()

            return security_settings;
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"Failed to fetch metadata: {str(e)}")
        return None

def analyze_metadata(metadata, metadata_type):
    # openai.api_key = OPENAI_API_KEY
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    prompt = f"Analyze the following Salesforce {metadata_type} metadata and provide recommendations for improvement:\n\n{metadata}"

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful Salesforce system administrator and security expert."},
                {"role": "user", "content": prompt}
            ]
        )
        print(completion.choices[0].message)
        return completion.choices[0].message
        # response = openai.Completion.create(
        #     engine="text-davinci-002",
        #     prompt=prompt,
        #     max_tokens=500,
        #     n=1,
        #     stop=None,
        #     temperature=0.7,
        # )
        # return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Failed to analyze metadata: {str(e)}")
        return None

st.title("Salesforce Security Scanner ")

sf = connect_to_salesforce()
if sf:
    st.success("Connected to Salesforce successfully!")

    metadata_types = ["SecuritySettings", "Profile", "PermissionSet", "Role"]
    selected_type = st.selectbox("Select metadata type", metadata_types)

    if st.button("Get Metadata"):
        metadata = fetch_metadata(sf, selected_type)
        if metadata:
            st.subheader(f"{selected_type} Metadata")
            st.json(metadata)

            analysis = analyze_metadata(metadata, selected_type)
            st.subheader("OpenAI Analysis")
            st.write(analysis.content)
else:
    st.error("Failed to connect to Salesforce. Please check your credentials.")

# if __name__ == "__main__":
#     main()