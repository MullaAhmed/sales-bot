-- Sample seed data for testing

-- Create a test company
INSERT INTO companies (id, name) VALUES
    ('acme-store', 'Acme Store')
ON CONFLICT (id) DO NOTHING;

-- Sample products
INSERT INTO products (company_id, name, sku, description, price, stock) VALUES
    ('acme-store', 'Wireless Mouse', 'WM-001', 'Ergonomic wireless mouse with USB receiver', 29.99, 150),
    ('acme-store', 'Mechanical Keyboard', 'KB-002', 'RGB mechanical keyboard with blue switches', 89.99, 75),
    ('acme-store', 'USB-C Hub', 'HB-003', '7-in-1 USB-C hub with HDMI and SD card reader', 49.99, 200),
    ('acme-store', 'Laptop Stand', 'LS-004', 'Adjustable aluminum laptop stand', 39.99, 100),
    ('acme-store', 'Webcam HD', 'WC-005', '1080p HD webcam with built-in microphone', 59.99, 50)
ON CONFLICT DO NOTHING;

-- Sample order with shipment
INSERT INTO orders (id, company_id, customer_email, status, total) VALUES
    ('22222222-2222-2222-2222-222222222222', 'acme-store', 'customer@example.com', 'shipped', 119.98)
ON CONFLICT (id) DO NOTHING;

INSERT INTO shipments (order_id, carrier, tracking_number, status, estimated_delivery) VALUES
    ('22222222-2222-2222-2222-222222222222', 'FedEx', 'FX123456789', 'in_transit', CURRENT_DATE + INTERVAL '3 days')
ON CONFLICT DO NOTHING;
