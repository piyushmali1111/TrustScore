# TrustScore - Digital Trust Assurance System

![TrustScore Banner](https://img.shields.io/badge/TrustScore-v1.0-blue?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?style=flat-square&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**TrustScore** is an advanced analytics platform designed to revolutionize e-commerce trust. By moving beyond simple star ratings, it leverages machine learning to evaluate seller reliability through multi-dimensional behavioral metrics, ensuring a transparent and manipulation-resistant marketplace.

---

## 🎯 The Problem
Traditional 5-star rating systems are flawed. They are easily manipulated by fake reviews, fail to reflect logistical performance (like delivery speed), and do not provide a holistic view of seller reliability. Buyers need more than just an opinion; they need data-driven trust.

## 💡 The Solution
**TrustScore** aggregates six key performance indicators into a single, transparent score (0-100). Our engine processes transaction history, review text, and delivery logs to provide an unbiased assessment of every seller.

---

## ✨ Key Features

### 🛡️ **Advanced Fraud Detection**
- **Review Burst Analysis**: Automatically flags suspicious spikes in review volume (e.g., 5+ identical reviews in 24h).
- **Sentiment & Pattern Matching**: Identifies generic, low-effort spam reviews.
- **Short-Text Filtering**: Discards non-informative "one-word" 5-star ratings from the score calculation.

### 📊 **Multi-Dimensional Scoring Engine**
A weighted algorithm that prioritizes what matters most:
- **Delivery Performance (25%)**: On-time vs. late deliveries.
- **Authenticity (20%)**: Ratio of genuine to suspicious reviews.
- **Return Rate (20%)**: Indicator of product quality accuracy.
- **Response Time (15%)**: Speed of customer service.
- **Consistency (10%)**: Stability of performance over time.
- **Account Tenure (10%)**: Seller experience and longevity.

### 📈 **Interactive Analytics Dashboard**
- **Real-time Monitoring**: Live tracking of platform-wide trust levels.
- **Seller Profiles**: Detailed radar charts for individual seller analysis.
- **Risk Classification**: Automatic categorization of sellers into Low, Medium, and High Risk.

---

## 🛠️ Technology Stack

### **Backend Core**
- **FastAPI**: High-performance, async-ready Python web framework.
- **Pandas & NumPy**: Optimized for high-speed data processing.
- **Scikit-learn**: Powers the anomaly detection and text vectorization models.
- **Uvicorn**: Lightning-fast ASGI server implementation.

### **Frontend Interface**
- **HTML5 & CSS3**: Semantic structure with a modern, responsive design.
- **Vanilla JavaScript**: Lightweight, dependency-free interaction logic.
- **Chart.js**: Dynamic data visualization for dashboard analytics.

---

## 📁 Project Structure

```bash
TrustScore/
├── backend/
│   ├── main.py              # API Gateway & Route Handlers
│   ├── trust_engine.py      # Core Scoring Algorithms
│   ├── model.py             # ML Models for Fraud Detection
│   └── data_loader.py       # Data Ingestion Utilities
├── frontend/
│   ├── index.html           # Main Admin Dashboard
│   ├── seller.html          # Seller Profile View
│   ├── style.css            # Responsive Design System
│   └── script.js            # Frontend Logic & API Integration
├── data/
│   ├── sellers.csv          # Merchant Database
│   ├── orders.csv           # Transaction Records
│   └── reviews.csv          # Sentiment Data
└── requirements.txt         # Dependency Manifest
```

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8 or higher
- pip (Python Package Manager)

### **Installation**

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/TrustScore.git
    cd TrustScore
    ```

2.  **Set Up Virtual Environment**
    ```bash
    python -m venv venv
    
    # Windows
    .\venv\Scripts\activate
    
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch the Application**
    ```bash
    python -m uvicorn backend.main:app --reload
    ```
    The server will start at `http://localhost:8000`.

---

## 📊 Usage Guide

1.  **Dashboard**: Navigate to `http://localhost:8000/index.html` for a platform overview.
2.  **Seller Analysis**: Click on "Seller List" to view and sort merchants by Trust Score.
3.  **Deep Dive**: Select any seller to view their **Radar Chart** breakdown, revealing specific strengths and weaknesses (e.g., "Great Delivery, Poor Authenticity").

---

## 🔮 Roadmap

- [ ] **Database Migration**: Move from CSV to PostgreSQL for production scale.
- [ ] **Auth System**: Implement JWT-based secure login for admins.
- [ ] **Advanced NLP**: Upgrade fake review detection to use Transformers (BERT).
- [ ] **Real-time Alerts**: Webhook notifications for sudden drops in seller scores.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
