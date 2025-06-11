CREATE TABLE IF NOT EXISTS virtual_keys (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,              -- 例: page_location
    description TEXT,                       -- 例: 表示されたページのURL
    parent_field TEXT NOT NULL,             -- 例: event_params.key
    field_type TEXT NOT NULL,               -- STRING, INTEGER, FLOAT, BOOLEAN など
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);