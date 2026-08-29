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
    Calculate the basic sales metrics required Sy AIOS.
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
        "average_order_value": average_order_value,
    }
def parse_sales_csv(csv_data: bytes) -> dict:
    """
    Parse sales CSV bytes and return key AIOS sales metrics.
    """

    sales_df = pd.read_csv(BytesIO(csv_data))

    validation = validate_sales_columns(sales_df)

    if not validation["valid"]:
        raise ValueError(
            f"Missing required columns: {validation['missing_columns']}"
        )

    sales_df["Quantity"] = pd.to_numeric(
        sales_df["Quantity"],
        errors="raise",
    )

    sales_df["Price"] = pd.to_numeric(
        sales_df["Price"],
        errors="raise",
    )

    metrics = calculate_basic_metrics(sales_df)

    if sales_df.empty:
        metrics["best_selling_product"] = None
        metrics["worst_selling_product"] = None
        return metrics

    product_units = (
        sales_df.groupby("Product")["Quantity"]
        .sum()
    )

    metrics["best_selling_product"] = str(product_units.idxmax())
    metrics["worst_selling_product"] = str(product_units.idxmin())

    return metrics


