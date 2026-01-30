-- Seed data for Winston Electronics chatbot
-- Products are seeded from cleaned_products.csv via seed_products.py

-- Create the company
INSERT INTO companies (id, name) VALUES
    ('winston', 'Winston Electronics')
ON CONFLICT (id) DO UPDATE SET name = 'Winston Electronics';

-- Sample order for testing (optional)
INSERT INTO orders (id, company_id, customer_email, status, total) VALUES
    ('22222222-2222-2222-2222-222222222222', 'winston', 'customer@example.com', 'shipped', 3799.00)
ON CONFLICT (id) DO NOTHING;

INSERT INTO shipments (order_id, carrier, tracking_number, status, estimated_delivery) VALUES
    ('22222222-2222-2222-2222-222222222222', 'BlueDart', 'BD123456789', 'in_transit', CURRENT_DATE + INTERVAL '3 days')
ON CONFLICT DO NOTHING;
