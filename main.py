# Import necessary libraries
import streamlit as st
import pandas as pd
from pandas import ExcelWriter
import matplotlib.pyplot as plt
import base64

# Main function that runs the app
def main():
    st.title("AE Territory Realignment")
    
    # Load data
    data_file = st.file_uploader("Upload CSV", type=['csv'])
    if data_file is not None:
        data = load_data(data_file)
        display_data(data)
        
        # Select AEs
        ae_selection = select_aes(data)
        
        # If AE is selected
        if ae_selection:
            display_summary(data, ae_selection)
            
            if st.button('Export Results'):
                export_results(data)

# Loads and preprocesses the data
def load_data(file):
    data = pd.read_csv(file)
    return data

# Displays a subset of the data
def display_data(data):
    st.write(data.head())  # You can add a slider to control the number of rows displayed

# Allows users to select AEs
def select_aes(data):
    ae_list = data['AE'].unique().tolist()
    ae_selection = st.multiselect('Select AEs for realignment', ae_list)
    return ae_selection

# Display summary stats
def display_summary(data, ae_selection):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    
    # Number of accounts
    accounts_per_ae = data['AE'].value_counts()
    ax[0].bar(ae_selection, [accounts_per_ae[ae] for ae in ae_selection])
    ax[0].set_title('Number of Accounts')
    
    # Sales LFY
    sales_per_ae = data.groupby('AE')['Sales LFY'].sum()
    ax[1].bar(ae_selection, [sales_per_ae[ae] for ae in ae_selection])
    ax[1].set_title('Sales LFY')
    
    st.pyplot(fig)

# Export final results to Excel
def export_results(data):
    excel_file = 'results.xlsx'
    with ExcelWriter(excel_file) as writer:
        data.to_excel(writer, 'Account Assignments', index=False)
    st.markdown(get_table_download_link(excel_file), unsafe_allow_html=True)

# Get download link for the exported file
def get_table_download_link(file):
    with open(file, "rb") as f:
        bytes = f.read()
    b64 = base64.b64encode(bytes).decode()
    href = f'<a href="data:file/xlsx;base64,{b64}" download="{file}">Download results</a>'
    return href

# Run the app
if __name__ == "__main__":
    main()
