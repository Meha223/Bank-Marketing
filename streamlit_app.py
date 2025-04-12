import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from io import StringIO
import pyarrow.parquet as pq

# --- Load and Join Data ---
@st.cache_data
def load_data():
    fact = pd.read_parquet("marketing.parquet")
    client = pd.read_parquet("client.parquet")
    contact = pd.read_parquet("contact.parquet")
    campaign = pd.read_parquet("campaign.parquet")
    
    # Join all tables into one dataframe
    df = (
        fact.merge(client, on="fact_id", how="left")
            .merge(contact, on="fact_id", how="left")
            .merge(campaign, on="fact_id", how="left")
    )
    
    # Standardize 'subscribed' labels
    if df['subscribed'].dtype == 'int' or set(df['subscribed'].unique()) <= {0, 1}:
        df['subscribed_label'] = df['subscribed'].map({1: 'Subscribed', 0: 'Not Subscribed'})
    else:
        df['subscribed_label'] = df['subscribed'].astype(str).str.capitalize()
    
    return df

data = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["Exploratory Data Analysis", "SQL Query Interface"])

# --- Page 1: Exploratory Data Analysis ---
if page == "Exploratory Data Analysis":
    st.title("Exploratory Data Analysis (EDA)")

    # Display the raw data preview
    st.subheader("Data Preview")
    st.dataframe(data.head())

    # Show the summary statistics
    st.subheader("Summary Statistics")
    st.write(data.describe())

    # Visualizations
    # 1. Age group distribution
    age_group_count = data['age_group'].value_counts().reset_index()
    age_group_count.columns = ['Age Group', 'Count']
    fig = px.bar(age_group_count, x='Age Group', y='Count', title="Age Group Distribution")
    st.plotly_chart(fig)

    # 2. Campaign subscription analysis
    campaign_subscribed = data['subscribed'].value_counts().reset_index()
    campaign_subscribed.columns = ['Subscribed', 'Count']
    fig = px.pie(campaign_subscribed, names='Subscribed', values='Count', title="Subscription Distribution")
    st.plotly_chart(fig)

    # 3. Contact Duration vs Outcome
    fig = px.box(data, x='duration_length', y='subscribed', title="Contact Duration vs Subscription Outcome")
    st.plotly_chart(fig)

    # 4: Subscription Rate by Job
    st.subheader("💼 Subscription Rate by Job")
    job_subs = data.groupby(['job', 'subscribed_label']).size().reset_index(name='Count')
    fig = px.bar(job_subs, x='job', y='Count', color='subscribed_label',
                 title="Subscription Rate by Job", labels={'subscribed_label': 'Subscription'})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    # Filters to dynamically update the data
    age_group_filter = st.selectbox('Select Age Group:', data['age_group'].unique())
    filtered_data = data[data['age_group'] == age_group_filter]
    st.subheader(f"Filtered Data - Age Group: {age_group_filter}")
    st.write(filtered_data)

    st.subheader("Key Insights")
    st.markdown("""
    - The **Age Group** distribution shows the number of clients in different age groups.
    - **Campaign Subscription Distribution** shows how many people subscribed to the campaign.
    - **Contact Duration vs Outcome** gives insights into how the duration of the contact affects subscription outcomes.
    """)

# --- Page 2: SQL Query Interface ---
elif page == "SQL Query Interface":
    st.title("Data Query Interface")

    # Text box to enter SQL query
    query = st.text_area("Enter SQL Query", value="SELECT * FROM data LIMIT 10;", height=200)

    # Execute the SQL query
    @st.cache
    def execute_sql(query):
        try:
            # Using SQLite to run queries on the dataframe
            con = sqlite3.connect(":memory:")
            data.to_sql('data', con, index=False, if_exists='replace')
            result = pd.read_sql(query, con)
            con.close()
            return result
        except Exception as e:
            st.error(f"Error: {e}")
            return pd.DataFrame()

    # Display query results
    if query:
        result_data = execute_sql(query)
        st.subheader("Query Result Preview")
        st.dataframe(result_data.head())

        # Option to export data as CSV
        csv_data = result_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="query_result.csv",
            mime="text/csv"
        )
