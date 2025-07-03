import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("Albany Airbnb Dashboard")

# Load dataset
df = pd.read_csv("listings.csv")

# Clean room_type
df['room_type'] = df['room_type'].fillna('Unknown').str.strip()

# ✅ Clean price column (remove $, commas, and convert to float)
df['price'] = (
    df['price']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
)
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Clean review score column
df['review_scores_rating'] = pd.to_numeric(df['review_scores_rating'], errors='coerce')

# -- Sidebar Filters --
st.sidebar.header("🔎 Filter Listings")

# Room type filter
room_types = df['room_type'].dropna().unique().tolist()
selected_room_types = st.sidebar.multiselect("Select Room Type(s):", room_types, default=room_types)

# ✅ Drop missing prices before computing range
price_clean = df['price'].dropna()
if price_clean.empty:
    st.error("⚠️ No valid price data found in your file. Please check your listings.csv.")
    st.stop()

min_price = int(price_clean.min())
max_price = int(price_clean.max())

price_range = st.sidebar.slider("Select Price Range ($):", min_price, max_price, (min_price, 1000))

# Apply filters
filtered_df = df[
    (df['room_type'].isin(selected_room_types)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1])
]

# -- Chart 1: Room Type Distribution --
room_counts = filtered_df['room_type'].value_counts().reset_index()
room_counts.columns = ['room_type', 'count']

bar_chart = alt.Chart(room_counts).mark_bar().encode(
    x=alt.X('room_type:N', sort='-y', title='Room Type'),
    y=alt.Y('count:Q', title='Number of Listings'),
    color=alt.Color('room_type:N', legend=None)
).properties(
    title='Room Type Distribution',
    width=400,
    height=300
)

# -- Chart 2: Price Histogram --
hist = alt.Chart(filtered_df).mark_bar(opacity=0.7).encode(
    alt.X("price:Q", bin=alt.Bin(maxbins=50), title='Price ($)'),
    alt.Y('count()', title='Number of Listings'),
    tooltip=['count()']
).properties(
    title="Price Distribution (Filtered)",
    width=400,
    height=300
)

# -- Chart 3: Price vs Review Score Scatterplot --
scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
    x=alt.X('price:Q', title='Price ($)'),
    y=alt.Y('review_scores_rating:Q', title='Review Score'),
    color='room_type:N',
    tooltip=['name:N', 'price:Q', 'review_scores_rating:Q', 'room_type:N']
).properties(
    title="Price vs. Review Score by Room Type",
    width=800,
    height=400
).interactive()

# -- Display Dashboard --
col1, col2 = st.columns(2)
col1.altair_chart(bar_chart, use_container_width=True)
col2.altair_chart(hist, use_container_width=True)

st.altair_chart(scatter, use_container_width=True)

st.markdown("---")
st.write(f"**Showing {len(filtered_df)} listings out of {len(df)} total.**")
