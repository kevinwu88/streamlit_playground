import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from simple_salesforce import Salesforce
import os
import re

# Salesforce authentication
sf = Salesforce(
    username = st.secrets["sf_username"],
    password = st.secrets["sf_password"],
    security_token = st.secrets["sf_security_token"],
    domain = st.secrets["sf_domain"]  # Use 'test' for sandbox
)

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]

# Initialize ChatOpenAI
chat = ChatOpenAI(temperature=0)

# Initialize conversation memory
memory = ConversationBufferMemory(return_messages=True)

def identify_object_and_identifier(user_message):
    # Use the LLM to identify the object and identifier
    prompt = f"""
    Given the following user message, identify the Salesforce object (Case, Account, or Contact) and its unique identifier (Case Number, Account Name, or Contact Name).
    User message: {user_message}
    
    Respond in the following format:
    Object: [identified object]
    Identifier: [identified identifier]

    For Case Numbers, provide only the numeric part.
    """
    
    response = chat([HumanMessage(content=prompt)])

    print(response)
    
    # Extract object and identifier from the response
    object_match = re.search(r"Object: (.+)", response.content)
    identifier_match = re.search(r"Identifier: (.+)", response.content)
    
    object_name = object_match.group(1) if object_match else None
    identifier = identifier_match.group(1) if identifier_match else None
    
    return object_name, identifier

def get_record_details(object_name, search_term):
    try:
        if object_name == 'Case':
            record = sf.Case.get_by_custom_id('CaseNumber', search_term)
        elif object_name in ['Account', 'Contact']:
            query = f"SELECT Id, Name FROM {object_name} WHERE Name LIKE '%{search_term}%' LIMIT 1"
            result = sf.query(query)
            if result['totalSize'] > 0:
                record_id = result['records'][0]['Id']
                record = getattr(sf, object_name).get(record_id)
            else:
                return f"No {object_name} found with the name containing '{search_term}'"
        else:
            return f"Unsupported object: {object_name}"
        
        return record
    except Exception as e:
        return f"Error: {str(e)}"

def format_record_details(object_name, record):
    if isinstance(record, dict):
        if object_name == 'Case':
            return f"Case Number: {record.get('CaseNumber')}\n" \
                   f"Status: {record.get('Status')}\n" \
                   f"Subject: {record.get('Subject')}\n" \
                   f"Priority: {record.get('Priority')}\n" \
                   f"Description: {record.get('Description')}"
        elif object_name == 'Account':
            return f"Account Name: {record.get('Name')}\n" \
                   f"Industry: {record.get('Industry')}\n" \
                   f"Phone: {record.get('Phone')}\n" \
                   f"Website: {record.get('Website')}\n" \
                   f"Billing Address: {record.get('BillingStreet')}, {record.get('BillingCity')}, {record.get('BillingState')}, {record.get('BillingPostalCode')}, {record.get('BillingCountry')}"
        elif object_name == 'Contact':
            return f"Contact Name: {record.get('Name')}\n" \
                   f"Email: {record.get('Email')}\n" \
                   f"Phone: {record.get('Phone')}\n" \
                   f"Title: {record.get('Title')}\n" \
                   f"Account: {record.get('Account', {}).get('Name', 'N/A')}"
    return str(record)

st.title("Salesforce Record Search")

# Chat history
if 'messages' not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful assistant that can check Salesforce record details. When asked about a record, provide the information in a clear and concise manner.")
    ]

for message in st.session_state.messages[1:]:  # Skip the system message
    st.write(f"{'Human' if isinstance(message, HumanMessage) else 'Assistant'}: {message.content}")
    

# user_message = st.text_input("Your message:")

# if user_message:
#     st.session_state.messages.append(HumanMessage(content=user_message))
    
#     # Identify object and identifier from the user message
#     object_name, identifier = identify_object_and_identifier(user_message)
    
#     if object_name and identifier:
#         record_details = get_record_details(object_name, identifier)
#         formatted_details = format_record_details(object_name, record_details)
        
#         ai_prompt = f"Here are the details for {object_name} '{identifier}':\n\n{formatted_details}\n\nPlease summarize this information for the user."
#     else:
#         ai_prompt = user_message
    

#     # Get AI response
#     ai_response = chat([SystemMessage(content=f"You are a helpful assistant that can check Salesforce record details."),
#                         HumanMessage(content=ai_prompt)])
    
#     st.session_state.messages.append(AIMessage(content=ai_response.content))
#     st.chat_message("assistant").write(f"Assistant: {ai_response.content}")
#     # st.write(f"Assistant: {ai_response.content}")

#     # Update memory
#     memory.chat_memory.add_user_message(user_message)
#     memory.chat_memory.add_ai_message(ai_response.content)

# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

if user_message := st.chat_input():
    st.session_state.messages.append(HumanMessage(content=user_message))
    st.chat_message("user").write(user_message)
    
    # Identify object and identifier from the user message
    object_name, identifier = identify_object_and_identifier(user_message)
    
    if object_name and identifier:
        record_details = get_record_details(object_name, identifier)
        formatted_details = format_record_details(object_name, record_details)
        
        ai_prompt = f"Here are the details for {object_name} '{identifier}':\n\n{formatted_details}\n\nPlease summarize this information for the user."
    else:
        ai_prompt = user_message
    

    # Get AI response
    ai_response = chat([SystemMessage(content=f"You are a helpful assistant that can check Salesforce record details."),
                        HumanMessage(content=ai_prompt)])
    
    st.session_state.messages.append(AIMessage(content=ai_response.content))
    st.chat_message("assistant").write(f"Assistant: {ai_response.content}")
    # st.write(f"Assistant: {ai_response.content}")

    # Update memory
    memory.chat_memory.add_user_message(user_message)
    memory.chat_memory.add_ai_message(ai_response.content)