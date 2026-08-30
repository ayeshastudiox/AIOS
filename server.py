import io
import os
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from groq import Groq

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AIOS Executive Backend")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client securely
api_key = os.getenv("GROQ_API_KEY", "").strip()
groq_client = Groq(api_key=api_key) if api_key else None


class InsightsRequest(BaseModel):
    total_revenue: float
    total_units: int
    total_transactions: int
    top_product: Optional[str] = "N/A"
    bottom_product: Optional[str] = "N/A"
    category_breakdown: Optional[Dict[str, float]] = {}
    payment_breakdown: Optional[Dict[str, int]] = {}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only standard CSV files are supported.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        df.columns = df.columns.str.strip().str.lower()

        rev_col = next((c for c in df.columns if any(k in c for k in ["revenue", "sales", "price", "amount"])), None)
        qty_col = next((c for c in df.columns if any(k in c for k in ["unit", "quantity", "qty", "count"])), None)
        prod_col = next((c for c in df.columns if any(k in c for k in ["product", "item", "title", "name"])), None)
        cat_col = next((c for c in df.columns if any(k in c for k in ["category", "type", "group"])), None)
        pay_col = next((c for c in df.columns if any(k in c for k in ["payment", "channel", "method"])), None)

        if rev_col:
            df[rev_col] = pd.to_numeric(df[rev_col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0)
        else:
            df["computed_revenue"] = 0
            rev_col = "computed_revenue"

        if qty_col:
            df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(1)
        else:
            df["computed_qty"] = 1
            qty_col = "computed_qty"

        total_revenue = float(df[rev_col].sum())
        total_units = int(df[qty_col].sum())
        total_transactions = int(len(df))

        top_product = "N/A"
        bottom_product = "N/A"
        if prod_col and not df[prod_col].dropna().empty:
            prod_perf = df.groupby(prod_col)[rev_col].sum().sort_values(ascending=False)
            if not prod_perf.empty:
                top_product = str(prod_perf.index[0])
                bottom_product = str(prod_perf.index[-1])

        cat_breakdown = {}
        if cat_col and not df[cat_col].dropna().empty:
            cat_breakdown = df.groupby(cat_col)[rev_col].sum().round(2).to_dict()

        pay_breakdown = {}
        if pay_col and not df[pay_col].dropna().empty:
            pay_breakdown = df[pay_col].value_counts().to_dict()

        # Replaced "Cycle" with clean chronological Phase identifiers
        num_chunks = min(6, len(df))
        chunk_size = max(1, len(df) // num_chunks)
        
        chart_labels = []
        chart_values = []
        
        for i in range(num_chunks):
            chunk_slice = df.iloc[i * chunk_size : (i + 1) * chunk_size]
            chunk_val = float(chunk_slice[rev_col].sum())
            chart_values.append(round(chunk_val, 2))
            chart_labels.append(f"Phase {i+1}")

        return {
            "total_revenue": round(total_revenue, 2),
            "total_units": total_units,
            "total_transactions": total_transactions,
            "top_product": top_product,
            "bottom_product": bottom_product,
            "category_breakdown": cat_breakdown,
            "payment_breakdown": pay_breakdown,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/generate-insights")
async def generate_insights(payload: InsightsRequest):
    if not groq_client:
        return {"insights": "AI Error: GROQ_API_KEY missing or not found in .env file."}

    try:
        models_page = groq_client.models.list()
        active_model_ids = [m.id for m in models_page.data if hasattr(m, 'id')]

        if not active_model_ids:
            return {"insights": "AI Error: No active models returned from Groq."}

        selected_model = active_model_ids[0]

        top_prod = str(payload.top_product) if payload.top_product else "N/A"
        bot_prod = str(payload.bottom_product) if payload.bottom_product else "N/A"
        cat_data = str(payload.category_breakdown) if payload.category_breakdown else "{}"
        pay_data = str(payload.payment_breakdown) if payload.payment_breakdown else "{}"

        prompt = f"""
        You are an elite executive business strategist. Look at these metrics and output ONLY the final 3 bullet points. Do not include any thinking process, reasoning steps, calculations, or meta-commentary.

        Total Revenue: ${payload.total_revenue:,.2f}
        Total Units Sold: {payload.total_units:,}
        Total Transactions: {payload.total_transactions:,}
        Top Product: {top_prod}
        Bottom Product: {bot_prod}
        Categories: {cat_data}
        Payments: {pay_data}

        Format your response strictly as these three separate paragraphs with double line breaks:

        - **Revenue Dynamics Analysis**: Core sales driver evaluation based on the metrics.

        - **Operational Vulnerability**: Strategic risk or drag factor identified.

        - **Tactical Command Recommendation**: Concrete step to scale margin immediately.
        """

        completion = groq_client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700,
        )

        return {"insights": completion.choices[0].message.content}

    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return {"insights": f"AI Error: {str(e)}"}
    
# Locate directory structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend") if os.path.exists(os.path.join(BASE_DIR, "frontend")) else BASE_DIR

css_path = os.path.join(FRONTEND_DIR, "css")
js_path = os.path.join(FRONTEND_DIR, "js")

if os.path.exists(css_path):
    app.mount("/css", StaticFiles(directory=css_path), name="css")

if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")


@app.get("/")
async def read_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="index.html not found.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)