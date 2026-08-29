from io import BytesIO
import pandas as pd

# Supported column variations for schema flexibility
COLUMN_MAPPING = {
    "date": ["date", "Date"],
    "product": ["product_name", "product", "Product"],
    "quantity": ["units_sold", "quantity", "Quantity"],
    "price": ["unit_price", "price", "Price"],
    "revenue": ["total_revenue", "revenue", "Revenue"],
}

def parse_sales_csv(csv_data: bytes) -> dict:
    """
    Parse sales CSV bytes and return key AIOS sales metrics.
    """
    sales_df = pd.read_csv(BytesIO(csv_data))
    
    # Normalize column headers to lowercase for flexible matching
    lower_cols = {col.lower(): col for col in sales_df.columns}
    
    # Map dynamic column names
    product_col = next((lower_cols[alias] for alias in COLUMN_MAPPING["product"] if alias in lower_cols), None)
    qty_col = next((lower_cols[alias] for alias in COLUMN_MAPPING["quantity"] if alias in lower_cols), None)
    price_col = next((lower_cols[alias] for alias in COLUMN_MAPPING["price"] if alias in lower_cols), None)
    rev_col = next((lower_cols[alias] for alias in COLUMN_MAPPING["revenue"] if alias in lower_cols), None)

    # Validate essential columns exist
    if not (product_col and qty_col and (price_col or rev_col)):
        raise ValueError("CSV is missing required product, quantity, or price/revenue columns.")

    # Convert numeric fields
    sales_df[qty_col] = pd.to_numeric(sales_df[qty_col], errors="coerce").fillna(0)
    
    if rev_col:
        sales_df[rev_col] = pd.to_numeric(sales_df[rev_col], errors="coerce").fillna(0)
    else:
        sales_df[price_col] = pd.to_numeric(sales_df[price_col], errors="coerce").fillna(0)
        sales_df["total_revenue"] = sales_df[qty_col] * sales_df[price_col]
        rev_col = "total_revenue"

    # Calculate KPIs
    total_revenue = float(sales_df[rev_col].sum())
    total_units_sold = int(sales_df[qty_col].sum())
    total_transactions = int(len(sales_df))
    avg_order_value = round(total_revenue / total_transactions, 2) if total_transactions > 0 else 0.0

    product_units = sales_df.groupby(product_col)[qty_col].sum()
    best_selling = str(product_units.idxmax()) if not product_units.empty else None
    worst_selling = str(product_units.idxmin()) if not product_units.empty else None

    return {
        "total_revenue": total_revenue,
        "total_units_sold": total_units_sold,
        "total_transactions": total_transactions,
        "average_order_value": avg_order_value,
        "best_selling_product": best_selling,
        "worst_selling_product": worst_selling,
    }