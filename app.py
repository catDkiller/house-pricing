import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Streamlit Config ---
st.set_page_config(page_title="🏠 Retail Recommendation App", layout="wide")
st.title("🏠 Retail Recommendation App")
st.caption("Analyze properties and filter by price, grade, or recommendation type")

# --- Create Local Dataset ---
np.random.seed(42)  # for consistent results
n = 100

df = pd.DataFrame({
    'Date': pd.date_range(start='2025-01-01', periods=n, freq='D'),
    'Price': np.random.randint(50000, 500000, n),
    'Bedrooms': np.random.randint(1, 6, n),
    'Floors': np.random.choice([1, 2, 3], n),
    'Condition': np.random.choice([1, 2, 3, 4, 5], n),
    'Grade': np.random.randint(1, 13, n),
    'Year_Built': np.random.randint(1980, 2025, n),
    'Year_Renovated': np.random.choice([0, 2000, 2010, 2018, 2022], n)
})

# --- Recommendation Logic ---
price_median = df['Price'].median()
grade_median = df['Grade'].median()

df['per_bedroom'] = (df['Price'] / df['Bedrooms']).round()
df['Recommendation'] = 'Others'

df.loc[(df['Price'] <= price_median) & (df['Grade'] >= grade_median), 'Recommendation'] = 'Best'
df.loc[((df['Price'] <= price_median) & (df['Grade'] < grade_median)) |
       ((df['Price'] > price_median) & (df['Grade'] >= grade_median)), 'Recommendation'] = 'Decent'

if (df['Recommendation'] == 'Best').sum() == 0:
    best_idx = (df['Grade'] / df['Price']).idxmax()
    df.loc[best_idx, 'Recommendation'] = 'Best'

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

filter_type = st.sidebar.selectbox(
    "Choose Filter Type",
    ["Price Range", "Grade", "Recommendation Type"]
)

if filter_type == "Price Range":
    min_price, max_price = st.sidebar.slider(
        "Select Price Range",
        int(df['Price'].min()), int(df['Price'].max()),
        (int(df['Price'].min()), int(df['Price'].max()))
    )
    filtered_df = df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]

elif filter_type == "Grade":
    grades = sorted(df['Grade'].unique())
    selected_grade = st.sidebar.multiselect("Select Grade(s)", grades, default=grades)
    filtered_df = df[df['Grade'].isin(selected_grade)]

else:
    rec_types = df['Recommendation'].unique().tolist()
    selected_rec = st.sidebar.multiselect("Select Recommendation", rec_types, default=rec_types)
    filtered_df = df[df['Recommendation'].isin(selected_rec)]

# --- Display ---
st.subheader("📋 Filtered Data Sample")
st.dataframe(filtered_df.head())

st.subheader("📊 Recommendation Distribution")
st.bar_chart(filtered_df['Recommendation'].value_counts())

st.subheader("📈 Price vs Grade")
fig, ax = plt.subplots()
colors = {'Best': 'green', 'Decent': 'orange', 'Others': 'gray'}
ax.scatter(filtered_df['Grade'], filtered_df['Price'], c=filtered_df['Recommendation'].map(colors), alpha=0.6)
ax.set_xlabel('Grade')
ax.set_ylabel('Price')
ax.set_title('Price vs Grade by Recommendation')
st.pyplot(fig)

# --- Download Option ---
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered CSV", data=csv, file_name="filtered_data.csv", mime="text/csv")
