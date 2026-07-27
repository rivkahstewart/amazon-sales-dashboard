# Amazon Sales Dashboard

A Streamlit dashboard exploring the [Amazon Sales Dataset](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) from Kaggle — covering product pricing, discounts, ratings, and categories.

## Setup

1. Clone this repo and open it in a Codespace (or locally with WSL/Ubuntu).
2. Install `uv` if it isn't already available:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install dependencies:
   ```
   uv add pandas streamlit plotly
   ```
4. Download the dataset from Kaggle (link above, free account required) and place it at:
   ```
   data/raw/amazon.csv
   ```
   (This file is intentionally excluded from the repo via `.gitignore` — you'll need to download it yourself.)

## Running the dashboard

```
uv run streamlit run app.py
```

## Data Cleaning Decisions

The raw CSV has several fields that don't load cleanly as numbers by default:

- **`discounted_price` / `actual_price`** — stored as text with a `₹` symbol and thousands commas (e.g. `"₹1,099"`). Stripped both characters and cast to float.
- **`discount_percentage`** — stored as a percentage string (e.g. `"64%"`). Stripped the `%` sign and cast to float.
- **`rating`** — contains one non-numeric placeholder value (`"|"`) that breaks a naive numeric conversion. Coerced this value to `NaN` using `pd.to_numeric(errors="coerce")` rather than dropping the row, since only the rating column was affected — the row's price, category, and other fields are still valid and used elsewhere in the dashboard. `NaN` ratings are automatically excluded from rating-based calculations (like averages) by pandas, without losing that product from price or category charts.
- **`rating_count`** — contains thousands commas (e.g. `"24,269"`) and 2 missing values. Stripped commas and cast to numeric, letting the 2 missing values become `NaN` rather than guessing a value.
- **`category`** — stored as a pipe-delimited hierarchy (e.g. `"Electronics|Cables|USBCables"`). Extracted the top-level category into a new `main_category` column for cleaner grouping in charts, since the full hierarchy has too many unique combinations to chart meaningfully.

## Dataset

- 1,465 products
- Source: Amazon Sales Dataset, Kaggle
- Key fields used: category, discounted_price, actual_price, discount_percentage, rating, rating_count

## AI Tool Usage

See `AI_USE.md` for a detailed log of how AI tools were used throughout this project.
