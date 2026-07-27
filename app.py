import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Amazon Sales Dashboard", layout="wide")

# -----------------------------
# Load & clean data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/amazon.csv")

    # Prices: strip ₹ symbol and thousands commas, then convert to float
    for col in ["discounted_price", "actual_price"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

    # Discount percentage: strip % sign, convert to float
    df["discount_percentage"] = (
        df["discount_percentage"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .astype(float)
    )

    # Rating: contains a "|" placeholder for at least one row.
    # Coerce anything non-numeric to NaN rather than dropping the row,
    # since only the rating value itself is bad — the rest of that
    # row's data (price, category, etc.) is still usable.
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Rating count: strip commas, convert to float (keeps NaN for missing values)
    df["rating_count"] = (
        df["rating_count"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")

    # Primary category: the category field is a pipe-delimited hierarchy
    # (e.g. "Electronics|Cables|USBCables") — take the top-level category
    # for cleaner grouping in charts.
    df["main_category"] = df["category"].astype(str).str.split("|").str[0]

    return df

df = load_data()

# -----------------------------
# Header
# -----------------------------
st.title("Amazon Sales Dashboard")
st.write(
    "Explore product pricing, discounts, ratings, and categories from the "
    "Amazon Sales Dataset (Kaggle). Prices are in Indian Rupees (₹)."
)

with st.expander("Preview raw data"):
    st.dataframe(df.head(20))

# -----------------------------
# Summary metrics
# -----------------------------
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Products", f"{len(df):,}")
col2.metric("Average Rating", f"{df['rating'].mean():.2f} ⭐")
col3.metric("Average Discount", f"{df['discount_percentage'].mean():.0f}%")

st.divider()

# -----------------------------
# Chart 1: Products per category
# -----------------------------
st.subheader("Which categories have the most products?")
category_counts = (
    df["main_category"].value_counts().head(10).reset_index()
)
category_counts.columns = ["main_category", "count"]
fig1 = px.bar(
    category_counts,
    x="count",
    y="main_category",
    orientation="h",
    labels={"count": "Number of Products", "main_category": "Category"},
    title="Top 10 Categories by Product Count",
)
fig1.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig1, width='stretch')
st.write(
    f"**Takeaway:** {category_counts.iloc[0]['main_category']} leads with "
    f"{category_counts.iloc[0]['count']} products in this dataset. "
    "Product listings are concentrated in a handful of top categories, "
    "with a long tail of smaller ones."
)

st.divider()

# -----------------------------
# Chart 2: Average rating by category
# -----------------------------
st.subheader("Which categories have the highest average ratings?")
top_categories = df["main_category"].value_counts().head(10).index
rating_by_category = (
    df[df["main_category"].isin(top_categories)]
    .groupby("main_category")["rating"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
fig2 = px.bar(
    rating_by_category,
    x="rating",
    y="main_category",
    orientation="h",
    labels={"rating": "Average Rating", "main_category": "Category"},
    title="Average Rating by Category (Top 10 Categories by Volume)",
)
fig2.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig2, width='stretch')
st.write(
    "**Takeaway:** Average ratings across top categories are fairly close "
    "together, generally sitting between 3.8 and 4.3 stars, suggesting "
    "rating alone doesn't vary much by category — quality is fairly "
    "consistent across product types in this dataset."
)

st.divider()

# -----------------------------
# Chart 3: Actual vs discounted price
# -----------------------------
st.subheader("How do actual price and discounted price compare?")
fig3 = px.scatter(
    df,
    x="actual_price",
    y="discounted_price",
    color="discount_percentage",
    labels={
        "actual_price": "Actual Price (₹)",
        "discounted_price": "Discounted Price (₹)",
        "discount_percentage": "Discount %",
    },
    title="Actual vs Discounted Price",
    opacity=0.6,
)
st.plotly_chart(fig3, width='stretch')
st.write(
    "**Takeaway:** Discounted price tracks actual price closely at lower "
    "price points, but the gap widens for higher-priced products, meaning "
    "expensive items tend to carry steeper rupee-value discounts even when "
    "percentage discounts are similar."
)

st.divider()

# -----------------------------
# Chart 4: Are higher-rated products more expensive?
# -----------------------------
st.subheader("Are higher-rated products more expensive?")
fig4 = px.scatter(
    df.dropna(subset=["rating"]),
    x="rating",
    y="discounted_price",
    labels={"rating": "Rating", "discounted_price": "Discounted Price (₹)"},
    title="Rating vs Discounted Price",
    opacity=0.5,
)
st.plotly_chart(fig4, width='stretch')
st.write(
    "**Takeaway:** There's no strong visual relationship between rating "
    "and price — highly rated products show up across the full price "
    "range, suggesting customers rate based on value and satisfaction "
    "rather than price alone."
)
