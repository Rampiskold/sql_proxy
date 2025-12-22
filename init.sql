-- Sample tables for testing SQL Query Proxy API

CREATE TABLE dict_currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dict_currencies IS 'Currency reference dictionary';
COMMENT ON COLUMN dict_currencies.code IS 'ISO 4217 currency code';
COMMENT ON COLUMN dict_currencies.symbol IS 'Currency symbol (e.g., $, €)';

INSERT INTO dict_currencies (code, name, symbol) VALUES
    ('USD', 'US Dollar', '$'),
    ('EUR', 'Euro', '€'),
    ('RUB', 'Russian Ruble', '₽'),
    ('GBP', 'British Pound', '£'),
    ('JPY', 'Japanese Yen', '¥');

CREATE TABLE app_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE app_logs IS 'Application logs';

CREATE INDEX idx_logs_level ON app_logs(log_level);
CREATE INDEX idx_logs_created_at ON app_logs(created_at);

INSERT INTO app_logs (log_level, message) VALUES
    ('INFO', 'Application started'),
    ('ERROR', 'Database connection failed'),
    ('INFO', 'Request processed'),
    ('WARNING', 'High memory usage detected'),
    ('INFO', 'User logged in');
