USE canadian_market;

-- MySQL 8+. Each window restarts for each stock.
CREATE OR REPLACE VIEW daily_metrics AS
SELECT symbol, date, open, high, low, close, adj_close, volume,
    adj_close / LAG(adj_close) OVER w - 1 AS daily_return,
    CASE WHEN COUNT(*) OVER r = 30 THEN AVG(adj_close) OVER r END AS ma30,
    100 * adj_close / FIRST_VALUE(adj_close) OVER w AS indexed_value,
    adj_close / MAX(adj_close) OVER w - 1 AS drawdown
FROM prices
WINDOW w AS (PARTITION BY symbol ORDER BY date),
       r AS (PARTITION BY symbol ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW);

CREATE OR REPLACE VIEW stock_summary AS
SELECT c.symbol, c.company, c.sector, MIN(m.date) AS start_date,
    MAX(m.date) AS end_date, COUNT(*) AS observations,
    MAX(CASE WHEN m.date = b.end_date THEN m.adj_close END) /
      MAX(CASE WHEN m.date = b.start_date THEN m.adj_close END) - 1 AS period_return,
    AVG(m.volume) AS avg_daily_volume,
    STDDEV_SAMP(m.daily_return) * SQRT(252) AS annualized_volatility,
    MIN(m.drawdown) AS max_drawdown
FROM daily_metrics m
JOIN companies c ON c.symbol = m.symbol
JOIN (SELECT symbol, MIN(date) AS start_date, MAX(date) AS end_date
      FROM prices GROUP BY symbol) b ON b.symbol = m.symbol
GROUP BY c.symbol, c.company, c.sector;

-- Ranking over the full available period, not average daily return.
SELECT * FROM stock_summary ORDER BY period_return DESC;
SELECT symbol, avg_daily_volume FROM stock_summary ORDER BY avg_daily_volume DESC;

-- Equal-weight average of the chosen stocks' period returns, NOT an index.
SELECT sector, COUNT(*) AS sampled_stocks, AVG(period_return) AS sample_mean_return
FROM stock_summary GROUP BY sector ORDER BY sample_mean_return DESC;
