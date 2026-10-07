from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# A small hand-picked study sample, not a market index or sector benchmark.
COMPANIES = [
    ("RY.TO", "Royal Bank of Canada", "Financials"),
    ("TD.TO", "Toronto-Dominion Bank", "Financials"),
    ("ENB.TO", "Enbridge", "Energy"),
    ("CNQ.TO", "Canadian Natural Resources", "Energy"),
    ("SHOP.TO", "Shopify", "Technology"),
    ("CSU.TO", "Constellation Software", "Technology"),
    ("ABX.TO", "Barrick", "Materials"),
    ("AEM.TO", "Agnico Eagle Mines", "Materials"),
]
START = "2025-01-01"
END = "2026-01-01"  # Exclusive: the last requested day is December 31, 2025.
