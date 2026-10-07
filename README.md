# Canadian Stock Market Analytics

**End-to-End Financial Data Analytics Project | Python • MySQL • SQL • Power BI**

## Project Overview

This project is an end-to-end financial data analytics solution designed to analyze the performance and risk of publicly traded Canadian stocks on the Toronto Stock Exchange (TSX).

It demonstrates a complete data analytics workflow, from collecting and cleaning historical stock market data to storing it in a relational database, performing financial analysis, and developing interactive Power BI dashboards.

The goal is to transform raw financial data into meaningful insights that can support investment research and data-driven decision-making.

## Technologies Used

- **Python:** Data collection, cleaning, transformation, and financial calculations
- **Pandas & NumPy:** Data manipulation and statistical analysis
- **MySQL:** Relational database management and storage
- **SQL:** Financial data analysis and querying
- **Power BI:** Interactive dashboards and data visualization
- **Git & GitHub:** Version control and project documentation

## Key Features

- Automated historical stock price data collection
- Data cleaning and preprocessing using Python
- MySQL database integration
- Stock performance and return analysis
- Annualized volatility and risk analysis
- Maximum drawdown calculations
- Comparative analysis of Canadian stocks
- Interactive financial dashboards using Power BI

## Business Questions Answered

1. Which Canadian stocks generated the highest returns during the analyzed period?
2. Which stocks experienced the greatest price volatility?
3. How do the risk and returns of different stocks compare?
4. Which stocks experienced the largest peak-to-trough declines?
5. How did stock prices and performance change over time?
6. What insights can investors gain from historical market performance?

## Project Workflow

### 1. Data Collection

Retrieve historical Canadian stock market data using Python.

### 2. Data Cleaning

Process missing values, standardize datasets, and calculate financial performance metrics.

### 3. Database Integration

Load structured datasets into MySQL for persistent storage and querying.

### 4. Financial Analysis

Use Python and SQL to evaluate returns, volatility, maximum drawdown, and historical price trends.

### 5. Data Visualization

Build interactive Power BI dashboards to communicate financial insights and compare stock performance.

## Financial Metrics

| Metric | Description |
|---|---|
| **Period Return** | Percentage change in stock value over the analysis period |
| **Annualized Volatility** | Annualized standard deviation of daily stock returns |
| **Maximum Drawdown** | Largest percentage decline from a historical peak |
| **Daily Return** | Percentage change in closing price between trading days |

## Project Structure

```text
canadian-stock-market-analytics/
├── src/
│   ├── config.py
│   ├── download.py
│   ├── clean.py
│   └── load_mysql.py
├── sql/
│   ├── schema.sql
│   └── analysis.sql
├── data/
├── requirements.txt
└── README.md
```

## Skills Demonstrated

- End-to-end ETL pipeline development
- Financial data analysis
- Python programming and automation
- SQL querying and relational database design
- Data cleaning and transformation
- Business intelligence and dashboard development
- Financial risk and performance measurement

## Future Improvements

- Incorporate additional TSX-listed companies
- Add benchmark comparisons against Canadian market indices
- Automate periodic data updates
- Expand portfolio-level risk analysis
- Explore predictive analytics and forecasting

## Disclaimer

This project is intended for educational and portfolio purposes only. The financial analysis is based on historical market data and should not be considered investment advice.
