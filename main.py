# Import necessary libraries
import streamlit as st
import pandas as pd
from pandas import ExcelWriter
import matplotlib.pyplot as plt
import base64


# Main function that runs the app
def main():
    st.title("AE Territory Realignment")
    st.markdown("""
                ### Directions:
                1. Upload a CSV file with three columns in the following order: Account_ID, AE, Sales LFY.
                2. Select the AEs you want to consider for realignment.
                3. Use the reassignment tool to move accounts between AEs.
                4. The summary stats will update as you make changes.
                5. You can download the results by clicking on the 'Export Results' button.
                """)

    file = st.file_uploader("Upload data", type=['csv'])

    if file is not None:
        st.session_state.data = pd.read_csv(file)
        ae_list = st.session_state.data[st.session_state.data.columns[1]].unique().tolist()
        # Allow users to select AEs for consideration
        st.session_state.ae_selection = st.multiselect('Select AEs for Realignment:', options=list(st.session_state.data[st.session_state.data.columns[1]].unique()))

    if 'ae_selection' in st.session_state and st.session_state.ae_selection:
        # Display the selected AEs data
        selected_data = st.session_state.data[st.session_state.data[st.session_state.data.columns[1]].isin(st.session_state.ae_selection)]
        selected_data = realignment_interface(selected_data, st.session_state.ae_selection)
        st.dataframe(selected_data)

        # Display the summary statistics
        display_summary(selected_data, st.session_state.ae_selection)  # Pass selected_data here as well
    else:
        st.write("No AE selected for realignment. Please select at least one.")


# Adds an interface for account realignment
def realignment_interface(data, ae_selection):
    # Create a multi-column layout
    col1, col2 = st.columns(2)

    # Get unique account IDs
    accounts = data[data.columns[0]].unique().tolist()

    # SelectBox for account selection
    selected_account = col1.selectbox("Select Account", accounts)

    # SelectBox for AE selection
    selected_ae = col2.selectbox("Select AE", ae_selection)

    # Button to perform realignment
    if st.button('Reassign'):
        data.loc[data[data.columns[0]] == selected_account, data.columns[1]] = selected_ae
        st.success(f"Account {selected_account} has been reassigned to {selected_ae}!")

    return data  # Return updated DataFrame


def update_charts():
    # Trigger a rerun after AE selection
    st.experimental_rerun()


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
# Display summary stats
def display_summary(data, ae_selection):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))

    # Number of accounts
    accounts_per_ae = data.groupby(data.columns[1]).count()[data.columns[0]]
    bars1 = ax[0].bar(ae_selection, [accounts_per_ae[ae] for ae in ae_selection], color='skyblue')
    ax[0].set_title('Number of Accounts')

    # Add bar values
    for bar in bars1:
        yval = bar.get_height()
        ax[0].text(bar.get_x() + bar.get_width()/2, yval * 0.5, yval, ha='center', va='bottom', color='black', fontsize=12)

    # Sales LFY
    sales_per_ae = data.groupby(data.columns[1]).sum()[data.columns[2]]
    bars2 = ax[1].bar(ae_selection, [sales_per_ae[ae] for ae in ae_selection], color='skyblue')
    ax[1].set_title('Sales LFY')

    # Add bar values
    for bar in bars2:
        yval = bar.get_height()
        ax[1].text(bar.get_x() + bar.get_width()/2, yval * 0.5, round(yval, 2), ha='center', va='bottom', color='black', fontsize=12)

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
