import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Path to the CSV file where data will be saved (inside the data folder in root directory)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'expense_data.csv')

# Function to load data from the CSV file and ensure Date is in datetime format
def load_data():
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
        # Ensure the 'Date' column is in datetime format
        try:
            data['Date'] = pd.to_datetime(data['Date'])
        except Exception as e:
            st.error(f"Error converting dates: {e}")
        return data
    else:
        return pd.DataFrame(columns=['Date', 'Item', 'Category', 'Cost in EUR'])

# Function to save data to the CSV file
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Load the data from the CSV when the app starts
expense_data = load_data()

# Set page layout to wide
st.set_page_config(layout="wide")

# Load existing data to get unique items and categories
items = expense_data['Item'].unique().tolist()
categories = expense_data['Category'].unique().tolist()

# Initialize new_item and new_category to empty strings
new_item = ""
new_category = ""

# Sidebar for adding new grocery items
st.sidebar.header("Add New Expense Item")

# Sidebar with a collapsible expander
with st.sidebar.expander("Expense Inputs", expanded=False):

    # Date selection
    input_date = st.date_input("Enter the date", datetime.now())
    expense_data['Date'] = pd.to_datetime(expense_data['Date'], format='%d.%m.%Y').dt.date  # Convert to datetime.date

    # Dropdown for selecting existing items and categories
    selected_item = st.selectbox("Select item:", options=["", "Add Item"] + items)

    # Initialize category and cost variables
    selected_category = ""
    cost = 0.01

    # If an existing item is selected, get the related category and cost
    if selected_item not in ["", "Add Item"]:
        # Get the row(s) corresponding to the selected item
        item_data = expense_data[expense_data['Item'] == selected_item].iloc[0]
        selected_category = item_data['Category']
        cost = item_data['Cost in EUR']

    # Show the category dropdown, automatically selecting the corresponding category
    selected_category = st.selectbox("Select category:", options=["", "Add Category"] + categories, index=(
                categories.index(selected_category) + 2) if selected_category in categories else 0)

    # If Add Item is selected, then display input for a new item
    if selected_item == "Add Item":
        new_item = st.text_input("Enter a new item (if not listed):")

    # If Add Category is selected, then display input for a new category
    if selected_category == "Add Category":
        new_category = st.text_input("Enter a new category (if not listed):")

    # Show the cost input, pre-filled with the value if an existing item was selected
    cost = st.number_input("Enter cost in EUR", min_value=0.01, step=0.01, value=cost)

    # Button to add the item
    if st.button("Add Item"):
        item_to_add = new_item if new_item else selected_item
        category_to_add = new_category if new_category else selected_category

        # Check if "Add Item" or "Add Category" is selected
        if selected_item == "Add Item" and not new_item:
            st.error("Please fill in the new item field.")
        elif selected_category == "Add Category" and not new_category:
            st.error("Please fill in the new category field.")
        elif not item_to_add or not category_to_add:
            st.error("Please fill in both item and category.")
        else:
            # Create a new entry
            new_data = pd.DataFrame({
                'Date': [input_date],
                'Item': [item_to_add],
                'Category': [category_to_add],
                'Cost in EUR': [cost]
            })
            expense_data = pd.concat([expense_data, new_data], ignore_index=True)
            save_data(expense_data)  # Save the updated data
            st.success(f"{item_to_add} added under {category_to_add} with a cost of {cost} EUR")

# Dashboard title
st.markdown("<h1 style='text-align: center;'>Expense Dashboard</h1>", unsafe_allow_html=True)

# Add a divider
st.divider()

# Add a sidebar divider
st.sidebar.divider()

# Sidebar for adding new grocery items
st.sidebar.header("Analyze Expenses")

# Sidebar expander to analyze data
with st.sidebar.expander("Analyze expenses", expanded=False):
    # Date range selector for analysis
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")

    # Category selector
    unique_categories = expense_data['Category'].unique().tolist()
    selected_category = st.selectbox("Select Category", options=["All"] + unique_categories)

    # Filter items based on the selected category
    if selected_category != "All":
        filtered_items = expense_data[expense_data['Category'] == selected_category]['Item'].unique().tolist()
    else:
        filtered_items = expense_data['Item'].unique().tolist()

    # Item selector based on the filtered category
    selected_item = st.selectbox("Select Item", options=["All"] + filtered_items)

    # Filter data based on the selected date range, ensuring Date is comparable
    filtered_data = expense_data[
        (expense_data['Date'] >= start_date) &
        (expense_data['Date'] <= end_date)  # Include end date
        ]

    # Filter by selected category and item (if not 'All')
    if selected_category != "All":
        filtered_data = filtered_data[filtered_data['Category'] == selected_category]

    if selected_item != "All":
        filtered_data = filtered_data[filtered_data['Item'] == selected_item]

# Display total expenses
total_cost = filtered_data['Cost in EUR'].sum()
total_cost = round(total_cost, 2)
st.markdown("<h3 style='text-align: center;'>Total Expense</h1>",
                unsafe_allow_html=True)
st.markdown(f"<h2 style='color:red; font-weight: bold; text-align: center;'>{total_cost} €</h2>",
        unsafe_allow_html=True)

# Add a divider
st.divider()

# Columns for cost analysis over time and pie chart
col1, col2 = st.columns(2)

# Cost over time
with col1:
    st.markdown("<h3 style='text-align: center;'>Cost Over Time</h1>",
                unsafe_allow_html=True)

    # Group by date to get total cost per day
    cost_over_time = filtered_data.groupby('Date')['Cost in EUR'].sum().reset_index()

    # Create a line chart to show cost over time
    if not cost_over_time.empty:
        fig = px.line(cost_over_time, x='Date', y='Cost in EUR', title="Total Cost Over Time",
                      labels={'Cost in EUR': 'Total Cost (EUR)', 'Date': 'Date'})
        fig.update_traces(mode='lines+markers')  # Show both lines and markers
        # Format the x-axis to show only the date (DD.MM.YYYY)
        fig.update_xaxes(tickformat="%d.%m.%Y")
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected filters.")

# Bar chart Expense
with col2:
    st.markdown("<h3 style='text-align: center;'>Cost Bar Chart</h1>",
                unsafe_allow_html=True)

    # Check if the filtered data is not empty
    if not filtered_data.empty:
        # Determine whether to group by Item or Category based on selection
        if selected_category == "All":
            # Group by category to get costs for all categories
            category_cost = filtered_data.groupby('Category')['Cost in EUR'].sum().reset_index()

            # Sort the costs from high to low
            category_cost = category_cost.sort_values(by='Cost in EUR', ascending=False)

            # Format the cost values to two decimal points
            category_cost['Formatted Cost'] = category_cost['Cost in EUR'].map(lambda x: f"{x:.2f}")

            # Create bar chart with formatted cost values on the bars
            bar_fig = px.bar(category_cost, x='Category', y='Cost in EUR',
                             title="Total Cost by Category",
                             labels={'Cost in EUR': 'Total Cost in EUR'},
                             text='Formatted Cost')  # Use the formatted cost
            st.plotly_chart(bar_fig)

        else:
            # Group by item to get costs for all items in the selected category
            category_cost = filtered_data.groupby('Item')['Cost in EUR'].sum().reset_index()

            # Sort the costs from high to low
            category_cost = category_cost.sort_values(by='Cost in EUR', ascending=False)

            # Format the cost values to two decimal points
            category_cost['Formatted Cost'] = category_cost['Cost in EUR'].map(lambda x: f"{x:.2f}")

            # Create bar chart with formatted cost values on the bars
            bar_fig = px.bar(category_cost, x='Item', y='Cost in EUR',
                             title=f"Cost Breakdown for {selected_category}",
                             labels={'Cost in EUR': 'Total Cost in EUR'},
                             text='Formatted Cost')  # Use the formatted cost
            st.plotly_chart(bar_fig)

    else:
        st.write("Please adjust your filters to see the cost breakdown or the data is empty.")

# Add a divider
st.divider()

# Pie Chart
st.markdown("<h3 style='text-align: center;'>Categorical Expense</h1>",
            unsafe_allow_html=True)

# Check if the filtered data is not empty
if not filtered_data.empty:
    # Determine whether to group by Item or Category based on selection
    if selected_category == "All":
        # Group by category to get costs for all categories
        category_cost = filtered_data.groupby('Category')['Cost in EUR'].sum().reset_index()
        fig = px.pie(category_cost, values='Cost in EUR', names='Category',
                     title="Total Cost by Category")  # Display costs by category
    else:
        # Group by item to get costs for all items in the selected category
        category_cost = filtered_data.groupby('Item')['Cost in EUR'].sum().reset_index()
        fig = px.pie(category_cost, values='Cost in EUR', names='Item',
                     title=f"Cost Breakdown for {selected_category}")  # Display costs by item in selected category

    fig.update_traces(textinfo='percent+label+value')  # Show percentage, label, and value
    st.plotly_chart(fig)
else:
    st.write("Please adjust your filters to see the cost breakdown or the data is empty.")

# Add a divider
st.divider()

# Display filtered grocery data
st.subheader("Expense Data")
st.dataframe(filtered_data)

# Add a divider
st.divider()

# Logic to delete an entry
st.subheader("Delete an Entry")
if not filtered_data.empty:
    selected_rows = st.multiselect("Select rows to delete:",
                                   options=filtered_data.index.tolist(),
                                   format_func=lambda
                                       x: f"{filtered_data.loc[x, 'Date']} - {filtered_data.loc[x, 'Item']} - {filtered_data.loc[x, 'Category']} - {filtered_data.loc[x, 'Cost in EUR']}")

    if st.button("Delete Selected Items"):
        grocery_data = expense_data.drop(selected_rows).reset_index(drop=True)
        save_data(grocery_data)  # Save the updated data
        st.success("Selected items deleted!")
else:
    st.write("No data available for the selected date range.")