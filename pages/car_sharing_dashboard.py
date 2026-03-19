import streamlit as st
import pandas as pd

st.title("🚗 Car Sharing Dashboard")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# -------------------------
# MERGE DATAFRAMES
# -------------------------
# trips.car_id → cars.id
trips_merged = trips.merge(
    cars,
    left_on="car_id",
    right_on="id"
)

# cars.city_id → cities.city_id
trips_merged = trips_merged.merge(
    cities,
    on="city_id"
)

# -------------------------
# CLEAN DATA
# -------------------------
trips_merged = trips_merged.drop(
    columns=["id_x", "id_y", "customer_id"],
    errors="ignore"
)

# -------------------------
# DATE TRANSFORMATION
# -------------------------
trips_merged["pickup_date"] = pd.to_datetime(
    trips_merged["pickup_time"]
).dt.date

# -------------------------
# SIDEBAR FILTER
# -------------------------
st.sidebar.header("Filters")

car_brands = st.sidebar.multiselect(
    "Select Car Brand",
    trips_merged["brand"].dropna().unique(),
    key="brand_filter"
)

if car_brands:
    trips_merged = trips_merged[
        trips_merged["brand"].isin(car_brands)
    ]

# -------------------------
# METRICS
# -------------------------
total_trips = len(trips_merged)

total_distance = trips_merged["distance"].sum()

top_car = (
    trips_merged.groupby("model")["revenue"]
    .sum()
    .idxmax()
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Trips", total_trips)

with col2:
    st.metric("Top Car Model by Revenue", top_car)

with col3:
    st.metric("Total Distance (km)", f"{total_distance:,.2f}")

# -------------------------
# DATA PREVIEW
# -------------------------
st.subheader("Dataset Preview")
st.write(trips_merged.head())

# -------------------------
# VISUALIZATIONS
# -------------------------

# 1. Trips over time
st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size()
st.line_chart(trips_over_time)

# 2. Revenue per car model
st.subheader("Revenue per Car Model")
revenue_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_model)

# 3. Trips per city
st.subheader("Trips per City")
trips_city = trips_merged.groupby("city_name").size()
st.bar_chart(trips_city)

# BONUS: cumulative revenue
st.subheader("Cumulative Revenue Growth")
revenue_time = (
    trips_merged.groupby("pickup_date")["revenue"]
    .sum()
    .cumsum()
)
st.area_chart(revenue_time)