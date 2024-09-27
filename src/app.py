import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# region Path file definition
# Path to the CSV file where data will be saved (inside the data folder in root directory)
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'expense_data.csv')
DATA_FILE_BUDGET = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'budget_data.csv')
DATA_FILE_INCOME = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'income_data.csv')
# endregion Path file definition

# region Function for creating filtered df
def filter_dataframe(df, col_filters=None, date_range=None, date_col=None):
    # Copying df
    filtered_df = df.copy()

    # Applying col filters
    if col_filters:
        for col, values in col_filters.items():
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    # Apply date range filters if provided
    if date_range:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df[date_col] >= pd.to_datetime(start_date)) &
                                  (filtered_df[date_col] <= pd.to_datetime(end_date))]

    # Return filtered df
    return filtered_df
# endregion Function for creating filtered df

# region Functions for loading and saving expense csv
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
# endregion Functions for loading and saving expense csv

# region Functions for loading and saving budget csv
# Function to load budget data
def load_budget_data():
    if os.path.exists(DATA_FILE_BUDGET):
        data = pd.read_csv(DATA_FILE_BUDGET)
        # Ensure the 'Month' and 'Year' columns are in the appropriate format
        try:
            data['Month'] = data['Month'].astype(int)  # Ensure Month is int
            data['Year'] = data['Year'].astype(int)    # Ensure Year is int
        except Exception as e:
            st.error(f"Error converting dates: {e}")
        return data
    else:
        # Create a DataFrame with empty 'Month', 'Year', 'Category', and 'Budget' columns
        return pd.DataFrame(columns=['Month', 'Year', 'Item', 'Category', 'Budget'])

# Function to save budget data to the CSV file
def save_budget_data(budget_data):
    budget_data.to_csv(DATA_FILE_BUDGET, index=False)
# endregion Functions for loading and saving expense csv

# region Functions for loading and saving income csv
# Function to load income data
def load_income_data():
    if os.path.exists(DATA_FILE_INCOME):
        data = pd.read_csv(DATA_FILE_INCOME)
        # Ensure the 'Month' and 'Year' columns are in the appropriate format
        try:
            data['Month'] = data['Month'].astype(int)  # Ensure Month is int
            data['Year'] = data['Year'].astype(int)    # Ensure Year is int
        except Exception as e:
            st.error(f"Error converting dates: {e}")
        return data
    else:
        # Create a DataFrame with empty 'Month', 'Year', 'Category', and 'Budget' columns
        return pd.DataFrame(columns=['Month', 'Year', 'Category', 'Income'])

# Function to save budget data to the CSV file
def save_income_data(income_data):
    income_data.to_csv(DATA_FILE_INCOME, index=False)
# endregion Functions for loading and saving income csv

# region Load the data from the CSV when the app starts
expense_data = load_data()
budget_data = load_budget_data()
income_data = load_income_data()
# endregion region Load the data from the CSV when the app starts

# region Set page layout to wide
st.set_page_config(layout="wide")
# endregion region Set page layout to wide

# region Load existing data to get unique items and categories
items = expense_data['Item'].unique().tolist()
categories = expense_data['Category'].unique().tolist()
budget_items = budget_data['Item'].unique().tolist()
budget_categories = budget_data['Category'].unique().tolist()
# endregion Load existing data to get unique items and categories

# region Initialize new_item and new_category to empty strings
new_item = ""
new_budget_item = ""
new_category = ""
new_budget_category = ""
new_income_category = ""
# endregion region Initialize new_item and new_category to empty strings

# region Add new columns

# Check if 'Currency' column is present in expense data
if 'Currency' not in expense_data.columns:
    # Add 'Currency' column with default value None
    expense_data['Currency'] = None

# Check if 'Currency' column is present in budget data
if 'Currency' not in budget_data.columns:
    # Add 'Currency' column with default value None
    budget_data['Currency'] = None

# Check if 'Currency' column is present in income data
if 'Currency' not in income_data.columns:
    # Add 'Currency' column with default value None
    income_data['Currency'] = None

# endregion Add new columns

# region Expenses

st.sidebar.header("Expense")

# region Expense entry logic

# Sidebar with a collapsible expander
with st.sidebar.expander("Add Expense", expanded=False):
    # Date selection
    input_date = st.date_input("Enter Date", datetime.now())
    expense_data['Date'] = pd.to_datetime(expense_data['Date'], format='%d.%m.%Y').dt.date  # Convert to datetime.date

    # Dropdown for selecting existing items and categories
    selected_item = st.selectbox("Select Item:", options=["", "Add Item"] + items)

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
    selected_category = st.selectbox("Select Category:", options=["", "Add Category"] + categories, index=(
                categories.index(selected_category) + 2) if selected_category in categories else 0)

    # If Add Item is selected, then display input for a new item
    if selected_item == "Add Item":
        new_item = st.text_input("Enter a new item (if not listed):")

    # If Add Category is selected, then display input for a new category
    if selected_category == "Add Category":
        new_category = st.text_input("Enter a new category (if not listed):")

    # Show the cost input, pre-filled with the value if an existing item was selected
    cost = st.number_input("Enter Expense", min_value=0.01, step=0.01, value=cost)

    # Radio buttons for expense currency
    currency = st.radio('Expense Currency:', ['EUR', 'PKR'])

    # Check if expense is in EUR or PKR
    if currency == 'PKR':
        eur_pkr_rate = st.number_input("EUR to PKR", min_value=0.01, step=0.01, value=310.00)
        cost = round(cost / eur_pkr_rate, 2)

    # Custom CSS to make radio buttons appear side by side
    st.markdown(
        """
        <style>
        div.stRadio > div {
            display: flex;
            flex-direction: row;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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
                'Cost in EUR': [cost],
                'Currency': [currency]
            })
            expense_data = pd.concat([expense_data, new_data], ignore_index=True)
            save_data(expense_data)  # Save the updated data
            st.success(f"{item_to_add} added under {category_to_add} with a cost of {cost} in {currency}")
# endregion Expense entry logic

# region Analyze expenses logic

# Sidebar expander to analyze data
with st.sidebar.expander("Analyze expense", expanded=False):
    # Convert to datetime
    expense_data['Date'] = pd.to_datetime(expense_data['Date'], format='%d.%m.%Y', errors='coerce')

    # Extract days from the date
    expense_data['Day'] = expense_data['Date'].dt.day_name()

    # Get the earliest and latest dates
    min_date = expense_data['Date'].min().date()
    max_date = expense_data['Date'].max().date()

    # Date inputs in Streamlit with default values
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # Get date df
    df_date = filter_dataframe(expense_data, date_range=(start_date, end_date), date_col='Date')

    # Category selector
    unique_categories = df_date['Category'].unique()
    selected_categories = st.multiselect('Select Category', unique_categories, default=unique_categories)

    # Get filtered category df
    df_category = filter_dataframe(expense_data, col_filters={'Category': selected_categories},
                                   date_range=(start_date, end_date), date_col='Date')

    # Item selector
    unique_items = df_category['Item'].unique()
    selected_items = st.multiselect('Select Items', unique_items, default=unique_items)

    # Get filtered date & category df
    filtered_df = filter_dataframe(expense_data, col_filters={'Category': selected_categories,
                                                              'Item': selected_items},
                                   date_range=(start_date, end_date), date_col='Date')

    # Radio buttons for updating expense values
    update_expense_value = st.radio('Update Expense Conversion Rate?', ['No', 'Yes'])

    # Custom CSS to make radio buttons appear side by side
    st.markdown(
        """
        <style>
        div.stRadio > div {
            display: flex;
            flex-direction: row;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# endregion Analyze expenses logic

# endregion Expenses

# region Add a sidebar divider
st.sidebar.divider()
# endregion Add a sidebar divider

# region Dashboard title
st.markdown("<h1 style='text-align: center;'>Expense Dashboard</h1>", unsafe_allow_html=True)
# endregion Dashboard title

# region Add a divider
st.divider()
# endregion Add a divider

# region Budgets

st.sidebar.header("Budget")

# region Budget entry logic

# Sidebar expander to add budget
with st.sidebar.expander("Add Budget", expanded=False):
    # Get current year and month
    current_year = datetime.now().year
    years = list(range(current_year, current_year + 5))  # Adjust as needed
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Input for Month and Year
    selected_year = st.selectbox("Select Year", years)
    selected_month = st.selectbox("Select Month", month_names)

    # Dropdown for selecting existing budget items
    selected_budget_item = st.selectbox("Select Budget Item:", options=["", "Add Budget Item"] + budget_items)

    # Initialize category and cost variables
    selected_budget_category = ""
    budget = 0.01

    # If an existing item is selected, get the related category and budget
    if selected_budget_item not in ["", "Add Budget Item"]:
        # Get the row(s) corresponding to the selected item
        budget_item_data = budget_data[budget_data['Item'] == selected_budget_item].iloc[0]
        selected_budget_category = budget_item_data['Category']
        budget = budget_item_data['Budget']

    # Show the category dropdown, automatically selecting the corresponding category
    selected_budget_category = st.selectbox("Select Budget Category:", options=["", "Add Budget Category"] + budget_categories, index=(
                budget_categories.index(selected_budget_category) + 2) if selected_budget_category in budget_categories else 0)

    # If Add Budget Item is selected, then display input for a new budget item
    if selected_budget_item == "Add Budget Item":
        new_budget_item = st.text_input("Enter a new budget item (if not listed):")

    # If Add Budget Category is selected, then display input for a new budget category
    if selected_budget_category == "Add Budget Category":
        new_budget_category = st.text_input("Enter a new budget category (if not listed):")

    # Show the budget input, pre-filled with the value if an existing item was selected
    budget = st.number_input("Enter Budget", min_value=0.01, step=0.01, value=budget)

    # Radio buttons for expense currency
    currency = st.radio('Budget Currency:', ['EUR', 'PKR'])

    # Check if expense is in EUR or PKR
    if currency == 'PKR':
        eur_pkr_rate = st.number_input("EUR - PKR", min_value=0.01, step=0.01, value=310.00)
        budget = round(budget / eur_pkr_rate, 2)

    # Button to add the item
    if st.button("Add Budget Item"):
        # Convert month name to index (1-12)
        selected_month_index = month_names.index(selected_month) + 1

        # Check if "Add Budget Item" or "Add Budget Category" is selected
        budget_item_to_add = new_budget_item if new_budget_item else selected_budget_item
        budget_category_to_add = new_budget_category if new_budget_category else selected_budget_category
        if selected_budget_item == "Add Budget Item" and not new_budget_item:
            st.error("Please fill in the new budget item field.")
        elif selected_budget_category == "Add Budget Category" and not new_budget_category:
            st.error("Please fill in the new budget category field.")
        elif not budget_item_to_add or not budget_category_to_add:
            st.error("Please fill in both budget item and budget category.")
        else:
            # Create a new budget entry
            new_budget_entry = pd.DataFrame({
                'Month': [selected_month_index],
                'Year': [selected_year],
                'Item': [budget_item_to_add],
                'Category': [budget_category_to_add],
                'Budget': [budget],
                'Currency': [currency]
            })

            # Save budget entry
            budget_data = pd.concat([budget_data, new_budget_entry], ignore_index=True)
            save_budget_data(budget_data)  # Save the updated data
            st.success(f"Budget for {budget_item_to_add} under {budget_category_to_add} "
                       f"of {budget} added for {selected_month} {selected_year} in {currency}")
# endregion Budget entry logic

# endregion Budget

# region Add a sidebar divider
st.sidebar.divider()
# endregion Add a sidebar divider

# region Income

st.sidebar.header("Income")

# region Income entry logic

# Sidebar expander to add income
with st.sidebar.expander("Add Income", expanded=False):
    # Get current year and month
    current_year = datetime.now().year
    years = list(range(current_year, current_year + 5))  # Adjust as needed
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Initialize category and cost variables
    selected_income_category = ""
    selected_income = 0.01

    # Input for Month and Year
    selected_year_income = st.selectbox("Select Salary Year", years)
    selected_month_income = st.selectbox("Select Salary Month", month_names)

    # Logic for entering income category
    income_categories = income_data['Category'].unique().tolist()
    selected_income_category = st.selectbox("Select Income Category:", options=["", "Add Income Category"] + income_categories)
    if selected_income_category == "Add Income Category":
        new_income_category = st.text_input("Enter a new income category (if not listed):")

    # Logic for entering income
    if selected_income_category not in ["", "Add Income Category"]:
        income_category_data = income_data[income_data['Category'] == selected_income_category].iloc[0]
        selected_income = income_category_data['Income']
    selected_income = st.number_input("Enter Income Amount", min_value=0.01, step=0.01, value=selected_income)

    # Radio buttons for expense currency
    currency = st.radio('Income Currency:', ['EUR', 'PKR'])

    # Check if expense is in EUR or PKR
    if currency == 'PKR':
        eur_pkr_rate = st.number_input("EUR to PKR Rate", min_value=0.01, step=0.01, value=310.00)
        selected_income = round(selected_income / eur_pkr_rate, 2)

    if st.button("Add Income"):
        # Convert month name to index (1-12)
        selected_month_index = month_names.index(selected_month_income) + 1

        # Logic for adding the budget
        income_category_to_add = new_income_category if new_income_category else selected_income_category
        if selected_income_category == "Add Income Category" and not new_income_category:
            st.error("Please fill in the new income category field.")
        elif not income_category_to_add:
            st.error("Please select the income category.")
        else:
            # Create a new income entry
            new_income_entry = pd.DataFrame({
                'Month': [selected_month_index],
                'Year': [selected_year_income],
                'Category': [income_category_to_add],
                'Income': [selected_income],
                'Currency': [currency]
            })

            # Save budget entry
            income_data = pd.concat([income_data, new_income_entry], ignore_index=True)
            save_income_data(income_data)  # Save the updated data
            st.success(f"Income for {income_category_to_add} of {selected_income} added for "
                       f"{selected_month_income} {selected_year_income} in {currency}")
# endregion Income entry logic

# endregion Income

# region --- Expense Visualization ---
# Display total expenses
total_cost = filtered_df['Cost in EUR'].sum()
total_cost = round(total_cost, 2)
st.markdown("<h3 style='text-align: center;'>Total Expense</h1>",
                unsafe_allow_html=True)
st.markdown(f"<h2 style='color:red; font-weight: bold; text-align: center;'>{total_cost} €</h2>",
        unsafe_allow_html=True)
# endregion --- Expense Visualization ---

# region Add a divider
st.divider()
# endregion Add a divider

# region --- Hierarchical Chart ---
# Hierarchical chart
st.markdown("<h3 style='text-align: center;'>Hierachical Expense</h3>", unsafe_allow_html=True)

# Check if the filtered data is not empty
if not filtered_df.empty:
    fig = px.icicle(filtered_df, path=[px.Constant("All Expenses"), 'Category', 'Item', 'Day'],
                    values='Cost in EUR', color='Item', title='Hierarchical Expenses')
    fig.update_traces(texttemplate='%{label}<br>%{value} EUR', textinfo='label+text+value')
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig)
else:
    st.write("Please adjust your filters to see the cost breakdown or the data is empty.")
# endregion --- Hierarchical Chart ---

# region Add a divider
st.divider()
# endregion Add a divider

# region 2 Columns
col1, col2 = st.columns(2)
# endregion 2 Columns

# region --- Cost Over Time Chart ---
with col1:
    st.markdown("<h3 style='text-align: center;'>Expense Over Time</h1>",
                unsafe_allow_html=True)

    # Group by date to get total cost per day
    cost_over_time = filtered_df.groupby('Date')['Cost in EUR'].sum().reset_index()

    # Create a line chart to show cost over time
    if not cost_over_time.empty:
        fig = px.line(cost_over_time, x='Date', y='Cost in EUR', title="Expense Over Time",
                      labels={'Cost in EUR': 'Total Cost (EUR)', 'Date': 'Date'})
        fig.update_traces(mode='lines+markers')  # Show both lines and markers
        # Format the x-axis to show only the date (DD.MM.YYYY)
        fig.update_xaxes(tickformat="%d.%m.%Y")
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected filters.")
# endregion --- Cost Over Time Chart ---

# region --- Expense Bar Chart ---
with col2:
    st.markdown("<h3 style='text-align: center;'>Expense Bar Chart of Items</h1>",
                unsafe_allow_html=True)

    # Check if the filtered data is not empty
    if not filtered_df.empty:
            # Group by item to get costs for all items in the selected category
            category_cost = filtered_df.groupby('Item')['Cost in EUR'].sum().reset_index()

            # Sort the costs from high to low
            category_cost = category_cost.sort_values(by='Cost in EUR', ascending=False)

            # Format the cost values to two decimal points
            category_cost['Formatted Cost'] = category_cost['Cost in EUR'].map(lambda x: f"{x:.2f}")

            # Create bar chart with formatted cost values on the bars
            bar_fig = px.bar(category_cost, x='Item', y='Cost in EUR',
                             title=f"Items Expense Breakdown",
                             labels={'Cost in EUR': 'Total Cost in EUR'},
                             text='Formatted Cost')  # Use the formatted cost
            st.plotly_chart(bar_fig)

    else:
        st.write("Please adjust your filters to see the cost breakdown or the data is empty.")
# endregion --- Expense Bar Chart ---

# region Add a divider
st.divider()
# endregion Add a divider

# region --- Expense Data Overview ---

st.markdown("<h2 style='text-align: center;'>Expense Data Overview</h2>", unsafe_allow_html=True)

# Columns
col1, col2 = st.columns(2)

# Display filtered expense data
with col1:
    st.markdown("<h4 style='text-align: center;'>Expense Data</h4>", unsafe_allow_html=True)
    st.dataframe(filtered_df)

# Logic to delete an entry from expense data
with col2:
    st.markdown("<h4 style='text-align: center;'>Delete an Entry from the Expense Data</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        selected_rows = st.multiselect("Select rows to delete:",
                                       options=filtered_df.index.tolist(),
                                       format_func=lambda
                                           x: f"{filtered_df.loc[x, 'Date']} - {filtered_df.loc[x, 'Item']} - {filtered_df.loc[x, 'Category']} - {filtered_df.loc[x, 'Cost in EUR']} - "
                                              f"{filtered_df.loc[x, 'Currency']}")

        if st.button("Delete Expense Entry"):
            grocery_data = expense_data.drop(selected_rows).reset_index(drop=True)
            save_data(grocery_data)  # Save the updated data
            st.success("Selected items deleted!")
    else:
        st.write("No data available for the selected date range.")

    # Logic to edit the expense entry
    st.markdown("<h4 style='text-align: center;'>Edit an Entry from the Expense Data</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        # Allow user to select a row to edit, but no default selection
        selected_row = st.selectbox("Select a row to edit:",
                                    options=[None] + filtered_df.index.tolist(),  # Add 'None' as the default option
                                    format_func=lambda
                                        x: f"{filtered_df.loc[x, 'Date']} - {filtered_df.loc[x, 'Item']} - {filtered_df.loc[x, 'Category']} - {filtered_df.loc[x, 'Cost in EUR']} - "
                                           f"{filtered_df.loc[x, 'Currency']}" if x is not None else "Select a row")
        if selected_row is not None:
            # Display editable fields only when a row is selected
            selected_data = filtered_df.loc[selected_row]

            st.markdown("<h4 style='text-align: center;'>Edit Entry</h4>", unsafe_allow_html=True)

            # Allow user to edit the entry fields
            new_date = st.date_input("Edit Date", value=pd.to_datetime(selected_data['Date']))
            new_item = st.text_input("Edit Item", value=selected_data['Item'])
            new_category = st.text_input("Edit Category", value=selected_data['Category'])
            new_cost = st.number_input("Edit Cost (EUR)", value=selected_data['Cost in EUR'], step=0.01)
            new_currency = st.text_input("Edit Currency", value=selected_data['Currency'])

            if st.button("Save Changes"):
                # Update the selected row with new values
                expense_data.at[selected_row, 'Date'] = new_date.strftime('%Y-%m-%d')  # Convert to string if needed
                expense_data.at[selected_row, 'Item'] = new_item
                expense_data.at[selected_row, 'Category'] = new_category
                expense_data.at[selected_row, 'Cost in EUR'] = new_cost
                expense_data.at[selected_row, 'Currency'] = new_currency

                # Save the updated DataFrame
                save_data(expense_data)  # Function to save the DataFrame
                st.success("Entry updated successfully!")
    else:
        st.write("No data available for the selected date range.")

# endregion --- Expense Data Overview ---

# region Add a divider
st.divider()
# endregion Add a divider

# region --- Budget Data Overview ---

st.markdown("<h2 style='text-align: center;'>Budget Data Overview</h2>", unsafe_allow_html=True)

# Columns
col1, col2 = st.columns(2)

# Display filtered budget data
with col1:
    st.markdown("<h4 style='text-align: center;'>Budget Data</h4>", unsafe_allow_html=True)
    budget_data['Year'] = budget_data['Year'].astype(str)
    st.dataframe(budget_data)

# Logic to delete an entry from the budget data
with col2:
    st.markdown("<h4 style='text-align: center;'>Delete an Entry from the Budget Data</h4>", unsafe_allow_html=True)
    if not budget_data.empty:
        selected_rows = st.multiselect("Select rows to delete:",
                                       options=budget_data.index.tolist(),
                                       format_func=lambda
                                           x: f"{budget_data.loc[x, 'Month']} - {budget_data.loc[x, 'Year']} - {budget_data.loc[x, 'Item']} - "
                                              f"{budget_data.loc[x, 'Category']} - {budget_data.loc[x, 'Budget']} - "
                                              f"{budget_data.loc[x, 'Currency']}")

        if st.button("Delete Budget Entry"):
            budget_data = budget_data.drop(selected_rows).reset_index(drop=True)
            save_budget_data(budget_data)  # Save the updated data
            st.success("Selected items deleted!")
    else:
        st.write("No data available for the selected date range.")

    # Logic to edit the budget entry
    st.markdown("<h4 style='text-align: center;'>Edit an Entry from the Budget Data</h4>", unsafe_allow_html=True)
    if not budget_data.empty:
        # Allow user to select a row to edit, but no default selection
        selected_row = st.selectbox("Select a row to edit:",
                                    options=[None] + budget_data.index.tolist(),  # Add 'None' as the default option
                                    format_func=lambda
                                        x: f"{budget_data.loc[x, 'Month']} - {budget_data.loc[x, 'Year']} - {budget_data.loc[x, 'Item']} - "
                                           f"{budget_data.loc[x, 'Category']} - {budget_data.loc[x, 'Budget']} - "
                                           f"{budget_data.loc[x, 'Currency']}" if x is not None else "Select a row")

        if selected_row is not None:
            # Display editable fields only when a row is selected
            selected_data = budget_data.loc[selected_row]

            st.markdown("<h4 style='text-align: center;'>Edit Entry</h4>", unsafe_allow_html=True)

            # Allow user to edit the entry fields
            new_month = st.selectbox("Edit Month", options=[f"{i:02d}" for i in range(1, 13)], index=int(
                selected_data['Month']) - 1)  # Assuming month is in '01', '02', etc. format
            new_year = st.text_input("Edit Year", value=selected_data['Year'])
            new_item = st.text_input("Edit Item", value=selected_data['Item'])
            new_category = st.text_input("Edit Category", value=selected_data['Category'])
            new_budget = st.number_input("Edit Budget", value=selected_data['Budget'], step=0.01)
            new_currency = st.text_input("Edit Currency", value=selected_data['Currency'])

            if st.button("Save Changes"):
                # Update the selected row with new values
                budget_data.at[selected_row, 'Month'] = new_month
                budget_data.at[selected_row, 'Year'] = new_year
                budget_data.at[selected_row, 'Item'] = new_item
                budget_data.at[selected_row, 'Category'] = new_category
                budget_data.at[selected_row, 'Budget'] = new_budget
                budget_data.at[selected_row, 'Currency'] = new_currency

                # Save the updated DataFrame
                save_budget_data(budget_data)  # Function to save the updated data
                st.success("Budget entry updated successfully!")
    else:
        st.write("No data available for the selected date range.")
# endregion --- Budget Data Overview ---

# region Add a divider
st.divider()
# endregion Add a divider

# region --- Income Data Overview ---
st.markdown("<h2 style='text-align: center;'>Income Data Overview</h2>", unsafe_allow_html=True)

# Columns
col1, col2 = st.columns(2)

# Display filtered income data
with col1:
    st.markdown("<h4 style='text-align: center;'>Income Data</h4>", unsafe_allow_html=True)
    income_data['Year'] = income_data['Year'].astype(str)
    st.dataframe(income_data)

# Logic to delete an entry from the income data
with col2:
    st.markdown("<h4 style='text-align: center;'>Delete an Entry from the Income Data</h4>", unsafe_allow_html=True)
    if not income_data.empty:
        selected_rows = st.multiselect("Select rows to delete:",
                                       options=income_data.index.tolist(),
                                       format_func=lambda
                                           x: f"{income_data.loc[x, 'Month']} - {income_data.loc[x, 'Year']} - {income_data.loc[x, 'Category']} - "
                                              f"{income_data.loc[x, 'Income']} - {income_data.loc[x, 'Currency']}")

        if st.button("Delete Income Entry"):
            income_data = income_data.drop(selected_rows).reset_index(drop=True)
            save_income_data(income_data)  # Save the updated data
            st.success("Selected items deleted!")
    else:
        st.write("No data available for the selected date range.")

    # Logic to edit the income entry
    if not income_data.empty:
        # Allow user to select a row to edit, but no default selection
        selected_row = st.selectbox("Select a row to edit:",
                                    options=[None] + income_data.index.tolist(),  # Add 'None' as the default option
                                    format_func=lambda
                                        x: f"{income_data.loc[x, 'Month']} - {income_data.loc[x, 'Year']} - {income_data.loc[x, 'Category']} - "
                                           f"{income_data.loc[x, 'Income']} - {income_data.loc[x, 'Currency']}" if x is not None else "Select a row")

        if selected_row is not None:
            # Display editable fields only when a row is selected
            selected_data = income_data.loc[selected_row]

            st.write("### Edit Income Entry")
            st.markdown("<h4 style='text-align: center;'>Edit Entry</h4>", unsafe_allow_html=True)

            # Allow user to edit the entry fields
            new_month = st.selectbox("Edit Month", options=[f"{i:02d}" for i in range(1, 13)], index=int(
                selected_data['Month']) - 1)  # Assuming month is in '01', '02', etc. format
            new_year = st.text_input("Edit Year", value=selected_data['Year'])
            new_category = st.text_input("Edit Category", value=selected_data['Category'])
            new_income = st.number_input("Edit Income", value=selected_data['Income'], step=0.01)
            new_currency = st.text_input("Edit Currency", value=selected_data['Currency'])

            if st.button("Save Changes"):
                # Update the selected row with new values
                income_data.at[selected_row, 'Month'] = new_month
                income_data.at[selected_row, 'Year'] = new_year
                income_data.at[selected_row, 'Category'] = new_category
                income_data.at[selected_row, 'Income'] = new_income
                income_data.at[selected_row, 'Currency'] = new_currency

                # Save the updated DataFrame
                save_income_data(income_data)  # Function to save the updated data
                st.success("Income entry updated successfully!")
    else:
        st.write("No data available for the selected date range.")

# endregion --- Income Data Overview ---