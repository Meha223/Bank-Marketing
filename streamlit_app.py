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
    return df

data = load_data()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["Exploratory Data Analysis", "SQL Query Interface", "GenAI Assistant"])

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
    fig = px.box(
        data, 
        x='subscribed', 
        y='duration_length', 
        title="Contact Duration vs Subscription Outcome",
        labels={'subscribed': 'Subscribed', 'duration_length': 'Contact Duration'}
    )
    st.plotly_chart(fig)

    # 4. Contact Month Distribution
    st.subheader("Contact Month Distribution")
    month_count = data['month'].value_counts().sort_index().reset_index()
    month_count.columns = ['Month', 'Count']
    fig = px.bar(month_count, x='Month', y='Count', title="Contact Month Distribution")
    st.plotly_chart(fig)
    
    # 5. Subscription by Education
    st.subheader("Subscription Rate by Education Level")

    # Ensure 'subscribed' is boolean (if not already)
    data['subscribed'] = data['subscribed'].astype(bool)

    # Group and calculate subscription rate
    edu_group = data.groupby('education')['subscribed'].mean().reset_index()
    edu_group["Subscription Rate (%)"] = edu_group["subscribed"] * 100

    # Plot the results
    fig = px.bar(
        edu_group,
        x='education',
        y='Subscription Rate (%)',
        title="Subscription Rate by Education Level"
    )
    st.plotly_chart(fig)

    # 6. Subscription Rate by Age Group
    st.subheader("Subscription Rate by Age Group")

    # Ensure 'subscribed' is boolean
    data['subscribed'] = data['subscribed'].astype(bool)

    # Calculate subscription rate
    age_group = data.groupby('age_group')['subscribed'].mean().reset_index()
    age_group["Subscription Rate (%)"] = age_group["subscribed"] * 100

    # Pie Chart
    fig = px.pie(
        age_group,
        names='age_group',
        values='Subscription Rate (%)',
        title='Subscription Rate by Age Group'
    )
    st.plotly_chart(fig)

    # 7. Subscription Rate by Job
    st.subheader("Subscription Rate by Job (Bar Chart)")

    # Ensure 'subscribed' is boolean
    data['subscribed'] = data['subscribed'].astype(bool)

    # Calculate subscription rate
    job_group = data.groupby('job')['subscribed'].mean().reset_index()
    job_group["Subscription Rate (%)"] = job_group["subscribed"] * 100

    # Bar Chart
    fig = px.bar(
        job_group.sort_values("Subscription Rate (%)", ascending=True),
        x='Subscription Rate (%)',
        y='job',
        orientation='h',
        title='Subscription Rate by Job',
        labels={'job': 'Job', 'Subscription Rate (%)': 'Subscription Rate (%)'}
    )
    st.plotly_chart(fig)
    
    # Filters to dynamically update the data
    age_group_filter = st.selectbox('Select Age Group:', data['age_group'].unique())
    filtered_data = data[data['age_group'] == age_group_filter]
    st.subheader(f"Filtered Data - Age Group: {age_group_filter}")
    st.write(filtered_data)

    st.subheader("Key Insights")
    st.markdown("""
    - **Age Group Distribution**: 
      - The distribution of clients across different age groups is visualized. This can give an idea of which age groups are the most or least represented in the data.
      - This information is essential for understanding demographic trends and targeting specific age groups for campaigns.

    - **Campaign Subscription Distribution**:
      - This pie chart illustrates the proportion of people who subscribed to the campaign versus those who didn't. 
      - It provides a quick overview of campaign performance, showing how effective the campaign has been in driving subscriptions.

    - **Contact Duration vs Outcome**:
      - The box plot shows the relationship between the contact duration and the subscription outcome (whether the person subscribed or not). 
      - It can provide insights into whether longer contact durations lead to higher subscription rates or whether the outcome is independent of duration.
      - It may also highlight outliers in contact durations that resulted in different outcomes.

    - **Contact Month Distribution**:
      - This bar chart visualizes the distribution of contacts across different months. It helps identify seasonal trends or periods with higher or lower campaign activity or customer engagement.
      - It can be used to assess which months are most active for campaigns and where improvements may be needed.

    - **Subscription Rate by Education Level**:
      - This bar chart provides the subscription rate by education level. It can be used to assess whether certain education levels are more likely to subscribe to the campaign.
      - Understanding subscription trends by education level could help with targeted marketing efforts for specific educational demographics.

    - **Subscription Rate by Age Group**:
      - The pie chart shows the subscription rate by age group, indicating which age groups are more likely to subscribe to the campaign. 
      - This could help in tailoring future campaigns toward age groups with higher or lower subscription rates.

    - **Subscription Rate by Job**:
      - The bar chart shows the subscription rate by job type. This can help identify which job categories are more inclined to subscribe to the campaign. 
      - Understanding this information can be helpful for refining future campaigns, targeting specific professional groups for higher engagement.
    """)

# --- Page 2: SQL Query Interface ---    
# --- Convert Natural Language to SQL (basic simulation) ---
def prompt_to_sql(prompt):
     prompt = prompt.lower()

    if "campaign" in prompt and "age group" in prompt:
        return "SELECT * FROM data WHERE age_group = '30-40'"

      elif "show all data" in prompt or "all records" in prompt:
        return "SELECT * FROM data"

      elif "subscribed customers" in prompt:
        return "SELECT * FROM data WHERE subscribed = 1"

     elif "subscription rate by education" in prompt:
          return "SELECT education, AVG(subscribed) * 100 AS subscription_rate FROM data GROUP BY education"

      else:
          return "SELECT * FROM data LIMIT 10"
            
    elif page == "SQL Query Interface":

    # --- Page 3: Natural Language SQL Interface ---
    elif page == "Natural Language SQL":
        st.title("Natural Language SQL Exploration")

        user_prompt = st.text_input("Ask a question about the data:", "")

        if user_prompt:
            sql_query = prompt_to_sql(user_prompt)
            st.code(sql_query, language="sql")

            result = execute_sql(sql_query)

            if result.empty:
                st.warning("No results returned for this query.")
            else:
                st.dataframe(result)

     st.title("Data Query Interface")

    # Text box to enter SQL query
    query = st.text_area("Enter SQL Query", value="SELECT * FROM data LIMIT 10;", height=200)

    # Execute the SQL query
    @st.cache_data
    def execute_sql(query):
        try:
            # Using SQLite to run queries on the dataframe
            con = sqlite3.connect(":memory:")  # SQLite in-memory database
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

# --- Page 3: GenAI Assistant (Text-to-SQL Generator) ---
elif page == "GenAI Assistant":
    st.title("GenAI: Text-to-SQL Generator")

    st.markdown("""
    Type a natural language question, and I will try to generate the SQL query for you and run it on the dataset.
    """)

    user_question = st.text_input("Ask a question (e.g., 'Show all clients over age 50')")

    # Basic text-to-SQL logic (mocked)
    def generate_sql(natural_query):
        natural_query = natural_query.lower()
        if "clients over age" in natural_query:
            return "SELECT * FROM data WHERE age > 50"
        elif "subscription rate by job" in natural_query:
            return "SELECT job, AVG(CASE WHEN subscribed THEN 1 ELSE 0 END) * 100 AS subscription_rate FROM data GROUP BY job"
        elif "how many subscribed" in natural_query:
            return "SELECT COUNT(*) AS total_subscribed FROM data WHERE subscribed = 1"
        elif "subscription by education" in natural_query:
            return "SELECT education, COUNT(*) AS total, SUM(CASE WHEN subscribed THEN 1 ELSE 0 END) AS subscribed FROM data GROUP BY education"
        else:
            return "SELECT * FROM data LIMIT*"
