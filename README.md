# AIOS — AI Business Operating System Backend

AIOS is a high-performance FastAPI backend that ingests sales CSV data, processes core business KPIs, and generates automated strategic insights using Groq LLM.

---

## 🚀 Key Features

* **Data Upload Terminal:** Validates and stores sales CSV files securely.
* **Analytics Engine:** Parses transactional CSV data and calculates total revenue, units sold, transaction counts, and top/bottom selling products.
* **Groq AI Integration:** Automatically converts calculated business metrics into actionable business takeaways using LLM prompts.
* **Storage & Cleanup Management:** Background tasks automatically purge expired files after 24 hours.
* **Automated Test Suite:** Full unit coverage using `pytest` and `httpx`.

---

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Framework:** FastAPI
* **Data Processing:** Pandas
* **AI Provider:** Groq API
* **Testing:** Pytest & HTTPX
* **Server:** Uvicorn

---

## ⚙️ Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone <your-repo-url>
   cd AIOS