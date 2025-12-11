CREATE TABLE finance_stat (
  id SERIAL PRIMARY KEY,
  account VARCHAR(100),
  balance NUMERIC(18,2),
  updated_at TIMESTAMP DEFAULT now()
);

-- sample data
INSERT INTO finance_stat (account, balance) VALUES ('acct-001', 1000.00);

-- tạo publication để Debezium có thể đọc logical replication
CREATE PUBLICATION finance_pub FOR TABLE finance_stat;
