CREATE DATABASE IF NOT EXISTS canadian_market;
USE canadian_market;

CREATE TABLE IF NOT EXISTS companies (
    symbol VARCHAR(20) PRIMARY KEY,
    company VARCHAR(100) NOT NULL,
    sector VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS prices (
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DOUBLE NOT NULL,
    high DOUBLE NOT NULL,
    low DOUBLE NOT NULL,
    close DOUBLE NOT NULL,
    adj_close DOUBLE NOT NULL,
    volume BIGINT NOT NULL,
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES companies(symbol),
    CHECK (adj_close > 0),
    CHECK (volume >= 0)
);
