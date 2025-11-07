import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Streamlit Page Config ---
st.set_page_config(page_title="🏠 Retail Recommendation App", layout="wide")
st.title("🏠 Retail Recommendation App")
st.caption("Analyze properties and filter by price, grade, or recommendation type")

# --- Load Local Dataset ---
DATA_PATH = "archive.zip"
df = pd.read_csv(DATA_PATH, compression='zip' if DATA_PATH.endswith('.zip') else 'infer')

# --- Data Cleaning ---
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%dT%H%M%S', errors='coerce')

df = df.rename(columns={
    'date': 'Date', 'price': 'Price', 'bedrooms': 'Bedrooms', 'floors': 'Floors',
    'condition': 'Condition', 'grade': 'Grade', 'yr_built': 'Year_Built',
    'yr_renovated': 'Year_Renovated'
})

drop_cols = ['id', 'zipcode', 'sqft_living', 'sqft_lot', 'waterfront', 'view',
             'sqft_above', 'sqft_basement', 'lat', 'long', 'sqft_living15', 'sqft_lot15']
df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

df = df.dropna(subset=['Price', 'Grade', 'Bedrooms'])

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


# --- Sidebar Controls ---
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

else:  # Recommendation Type
    rec_types = df['Recommendation'].unique().tolist()
    selected_rec = st.sidebar.multiselect("Select Recommendation", rec_types, default=rec_types)
    filtered_df = df[df['Recommendation'].isin(selected_rec)]

# --- Display Results ---
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df.head())

st.subheader("📊 Recommendation Distribution (Filtered)")
st.bar_chart(filtered_df['Recommendation'].value_counts())

st.subheader("📈 Price vs Grade")
fig, ax = plt.subplots()
colors = {'Best': 'green', 'Decent': 'orange', 'Others': 'gray'}
ax.scatter(filtered_df['Grade'], filtered_df['Price'], c=filtered_df['Recommendation'].map(colors), alpha=0.6)
ax.set_xlabel('Grade')
ax.set_ylabel('Price')
ax.set_title('Price vs Grade by Recommendation')
st.pyplot(fig)

# --- Optional Download ---
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered CSV", data=csv, file_name="filtered_recommendations.csv", mime="text/csv")
