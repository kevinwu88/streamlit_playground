# data_analysis.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show():
    st.title("Data Analysis Page")
    
    # Sample data
    data = pd.DataFrame({
        'x': range(1, 11),
        'y': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    })
    
    st.write("Sample Data:")
    st.dataframe(data)
    
    st.write("Data Visualization:")
    fig, ax = plt.subplots()
    ax.scatter(data['x'], data['y'])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    st.pyplot(fig)