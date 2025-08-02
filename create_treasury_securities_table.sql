-- Create table to store on-the-run Treasury securities details
-- These are the actual bonds used to construct the yield curve

CREATE TABLE IF NOT EXISTS treasury_securities (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Security identification
    cusip TEXT NOT NULL,
    isin TEXT,
    security_type TEXT NOT NULL, -- 'Bill', 'Note', 'Bond'
    
    -- Security details
    maturity_date DATE NOT NULL,
    issue_date DATE NOT NULL,
    coupon_rate REAL NOT NULL,
    maturity_years REAL NOT NULL, -- 0.25, 0.5, 1, 2, 5, 10, 20, 30
    
    -- On-the-run status
    is_on_the_run BOOLEAN DEFAULT 1,
    became_on_the_run DATE NOT NULL,
    replaced_date DATE, -- When it became off-the-run
    
    -- Auction details
    auction_date DATE NOT NULL,
    auction_high_yield REAL,
    auction_size_billions REAL,
    
    -- Yield curve point
    curve_point TEXT NOT NULL, -- 'M3M', 'M2Y', 'M10Y', etc.
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(cusip)
);

-- Create view for current on-the-run securities
CREATE VIEW IF NOT EXISTS current_on_the_run AS
SELECT 
    curve_point,
    cusip,
    security_type,
    coupon_rate,
    issue_date,
    maturity_date,
    maturity_years,
    auction_date,
    ROUND(julianday(maturity_date) - julianday('now')) / 365.25 AS years_to_maturity
FROM treasury_securities
WHERE is_on_the_run = 1
ORDER BY maturity_years;

-- Create historical tracking table
CREATE TABLE IF NOT EXISTS treasury_curve_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curve_date DATE NOT NULL,
    curve_point TEXT NOT NULL,
    cusip TEXT NOT NULL,
    yield_percent REAL NOT NULL,
    price REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cusip) REFERENCES treasury_securities(cusip),
    UNIQUE(curve_date, curve_point)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_maturity_years ON treasury_securities(maturity_years);
CREATE INDEX IF NOT EXISTS idx_on_the_run ON treasury_securities(is_on_the_run, curve_point);
CREATE INDEX IF NOT EXISTS idx_issue_date ON treasury_securities(issue_date);
CREATE INDEX IF NOT EXISTS idx_curve_date ON treasury_curve_history(curve_date);