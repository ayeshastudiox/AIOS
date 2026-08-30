from datetime import timedelta
from io import BytesIO

import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Quantity",
    "Price",
    "Customer",
]


def validate_sales_columns(df: pd.DataFrame) -> dict:
    """
    Check whether the sales DataFrame contains
    all columns required by AIOS analytics.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns,
    }


def calculate_basic_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate the basic sales metrics required by AIOS.
    """

    validation = validate_sales_columns(df)

    if not validation["valid"]:
        raise ValueError(
            f"Missing required columns: {validation['missing_columns']}"
        )

    sales_df = df.copy()

    sales_df["Revenue"] = (
        sales_df["Quantity"] * sales_df["Price"]
    )

    total_revenue = float(sales_df["Revenue"].sum())
    total_units_sold = int(sales_df["Quantity"].sum())
    total_transactions = int(len(sales_df))

    average_order_value = (
        total_revenue / total_transactions
        if total_transactions > 0
        else 0.0
    )

    return {
        "total_revenue": total_revenue,
        "total_units_sold": total_units_sold,
        "total_transactions": total_transactions,
        "average_order_value": round(
            average_order_value,
            2,
        ),
    }


def parse_sales_csv(csv_data: bytes) -> dict:
    """
    Parse sales CSV bytes and return AIOS analytics metrics.
    """

    try:
        sales_df = pd.read_csv(BytesIO(csv_data))
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV file is empty.") from exc

    # Remove accidental spaces from column names
    sales_df.columns = sales_df.columns.str.strip()

    validation = validate_sales_columns(sales_df)

    if not validation["valid"]:
        raise ValueError(
            f"Missing required columns: {validation['missing_columns']}"
        )

    # Convert Quantity and Price into numbers
    sales_df["Quantity"] = pd.to_numeric(
        sales_df["Quantity"],
        errors="raise",
    )

    sales_df["Price"] = pd.to_numeric(
        sales_df["Price"],
        errors="raise",
    )

    metrics = calculate_basic_metrics(sales_df)

    # Handle a CSV that contains headers but no sales rows
    if sales_df.empty:
        metrics["customer_count"] = 0
        metrics["best_selling_product"] = None
        metrics["worst_selling_product"] = None
        metrics["top_customer"] = None
        metrics["product_revenue"] = {}
        metrics["product_units"] = {}

        metrics["sales_trend"] = {
            "labels": [],
            "revenue": [],
        }

        metrics["product_chart"] = {
            "labels": [],
            "revenue": [],
        }

        metrics["growth_percentage"] = 0.0
        metrics["prediction"] = {
            "next_date": None,
            "predicted_revenue": 0.0,
        }
        return metrics
    # -----------------------------
    # CUSTOMER ANALYTICS
    # -----------------------------

    metrics["customer_count"] = int(
        sales_df["Customer"].nunique()
    )

    customer_transactions = (
        sales_df.groupby("Customer")
        .size()
    )

    metrics["top_customer"] = str(
        customer_transactions.idxmax()
    )

    # -----------------------------
    # PRODUCT ANALYTICS
    # -----------------------------

    product_units = (
        sales_df.groupby("Product")["Quantity"]
        .sum()
    )

    metrics["best_selling_product"] = str(
        product_units.idxmax()
    )

    metrics["worst_selling_product"] = str(
        product_units.idxmin()
    )

    metrics["product_units"] = {
        str(product): int(units)
        for product, units in product_units.items()
    }

    product_revenue = (
        sales_df.assign(
            Revenue=sales_df["Quantity"] * sales_df["Price"]
        )
        .groupby("Product")["Revenue"]
        .sum()
    )

    metrics["product_revenue"] = {
        str(product): float(revenue)
        for product, revenue in product_revenue.items()
    }

    # Chart.js-ready product data
    metrics["product_chart"] = {
        "labels": list(
            metrics["product_revenue"].keys()
        ),
        "revenue": list(
            metrics["product_revenue"].values()
        ),
    }

    # -----------------------------
    # SALES TREND
    # -----------------------------

    sales_df["Date"] = pd.to_datetime(
        sales_df["Date"],
        errors="coerce",
    )

    dated_sales = sales_df.dropna(
        subset=["Date"]
    ).copy()

    dated_sales["Revenue"] = (
        dated_sales["Quantity"]
        * dated_sales["Price"]
    )

    daily_revenue = (
        dated_sales.groupby(
            dated_sales["Date"].dt.strftime(
                "%Y-%m-%d"
            )
        )["Revenue"]
        .sum()
        .sort_index()
    )

    metrics["sales_trend"] = {
        "labels": [
            str(date)
            for date in daily_revenue.index
        ],
        "revenue": [
            float(revenue)
            for revenue in daily_revenue.values
        ],
    }

    # -----------------------------
    # GROWTH PERCENTAGE
    # -----------------------------

    growth_percentage = 0.0

    if len(daily_revenue) >= 2:
        previous_revenue = float(
            daily_revenue.iloc[-2]
        )

        latest_revenue = float(
            daily_revenue.iloc[-1]
        )

        if previous_revenue != 0:
            growth_percentage = (
                (
                    latest_revenue
                    - previous_revenue
                )
                / previous_revenue
            ) * 100

    metrics["growth_percentage"] = round(
        growth_percentage,
        2,
    )
    # -----------------------------
    # SIMPLE SALES PREDICTION
    # -----------------------------

    prediction = {
        "next_date": None,
        "predicted_revenue": 0.0,
    }

    if len(daily_revenue) == 1:
        latest_revenue = float(
            daily_revenue.iloc[-1]
        )

        latest_date = pd.to_datetime(
            daily_revenue.index[-1]
        )

        prediction["next_date"] = (
            latest_date + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        prediction["predicted_revenue"] = round(
            latest_revenue,
            2,
        )

    elif len(daily_revenue) >= 2:
        revenue_values = [
            float(value)
            for value in daily_revenue.values
        ]

        changes = [
            revenue_values[index]
            - revenue_values[index - 1]
            for index in range(
                1,
                len(revenue_values),
            )
        ]

        average_change = (
            sum(changes) / len(changes)
        )

        predicted_revenue = (
            revenue_values[-1]
            + average_change
        )

        # Revenue prediction should not be negative
        predicted_revenue = max(
            predicted_revenue,
            0.0,
        )

        latest_date = pd.to_datetime(
            daily_revenue.index[-1]
        )

        prediction["next_date"] = (
            latest_date + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        prediction["predicted_revenue"] = round(
            predicted_revenue,
            2,
        )

    metrics["prediction"] = prediction

    return metrics
    return metrics