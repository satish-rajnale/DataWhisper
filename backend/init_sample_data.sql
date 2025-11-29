-- Sample database schema and data for Natural Language SQL Chat Application
-- Run this script to populate the database with sample tables and data

-- Create sample tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE users IS 'Stores user information';
COMMENT ON COLUMN users.name IS 'Full name of the user';
COMMENT ON COLUMN users.email IS 'Email address (unique)';
COMMENT ON COLUMN users.age IS 'Age of the user';
COMMENT ON COLUMN users.city IS 'City where user lives';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is active';

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS 'Product catalog';
COMMENT ON COLUMN products.name IS 'Product name';
COMMENT ON COLUMN products.category IS 'Product category';
COMMENT ON COLUMN products.price IS 'Product price in USD';
COMMENT ON COLUMN products.stock_quantity IS 'Available stock quantity';

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    shipping_address TEXT
);

COMMENT ON TABLE orders IS 'Customer orders';
COMMENT ON COLUMN orders.user_id IS 'Reference to the user who placed the order';
COMMENT ON COLUMN orders.total_amount IS 'Total order amount in USD';
COMMENT ON COLUMN orders.status IS 'Order status: pending, shipped, delivered, cancelled';

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

COMMENT ON TABLE order_items IS 'Items in each order';
COMMENT ON COLUMN order_items.quantity IS 'Quantity of product ordered';
COMMENT ON COLUMN order_items.unit_price IS 'Price per unit at time of order';
COMMENT ON COLUMN order_items.subtotal IS 'Total for this line item (quantity * unit_price)';

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE reviews IS 'Product reviews by users';
COMMENT ON COLUMN reviews.rating IS 'Rating from 1 to 5 stars';
COMMENT ON COLUMN reviews.comment IS 'Review text';

-- Insert sample data

-- Insert users
INSERT INTO users (name, email, age, city, is_active) VALUES
('John Doe', 'john.doe@example.com', 28, 'New York', TRUE),
('Jane Smith', 'jane.smith@example.com', 34, 'Los Angeles', TRUE),
('Bob Johnson', 'bob.johnson@example.com', 45, 'Chicago', TRUE),
('Alice Williams', 'alice.williams@example.com', 29, 'San Francisco', TRUE),
('Charlie Brown', 'charlie.brown@example.com', 52, 'Boston', TRUE),
('Diana Prince', 'diana.prince@example.com', 31, 'Seattle', TRUE),
('Eve Adams', 'eve.adams@example.com', 27, 'Austin', TRUE),
('Frank Miller', 'frank.miller@example.com', 38, 'Denver', FALSE),
('Grace Lee', 'grace.lee@example.com', 41, 'Portland', TRUE),
('Henry Davis', 'henry.davis@example.com', 33, 'Miami', TRUE);

-- Insert products
INSERT INTO products (name, category, price, stock_quantity, description) VALUES
('Laptop Pro 15"', 'Electronics', 1299.99, 25, 'High-performance laptop with 16GB RAM and 512GB SSD'),
('Wireless Mouse', 'Electronics', 29.99, 150, 'Ergonomic wireless mouse with long battery life'),
('Mechanical Keyboard', 'Electronics', 89.99, 45, 'RGB mechanical keyboard with Cherry MX switches'),
('Monitor 27" 4K', 'Electronics', 399.99, 30, 'Ultra HD 4K monitor with HDR support'),
('Coffee Maker', 'Appliances', 79.99, 60, 'Programmable coffee maker with thermal carafe'),
('Bluetooth Speaker', 'Electronics', 49.99, 80, 'Portable Bluetooth speaker with 20W output'),
('Desk Chair', 'Furniture', 199.99, 20, 'Ergonomic office chair with lumbar support'),
('Standing Desk', 'Furniture', 349.99, 15, 'Adjustable height standing desk'),
('Notebook Set', 'Office Supplies', 12.99, 200, 'Set of 3 premium notebooks'),
('Pen Set', 'Office Supplies', 24.99, 100, 'Premium pen set with 5 pens');

-- Insert orders
INSERT INTO orders (user_id, order_date, total_amount, status, shipping_address) VALUES
(1, '2024-01-15 10:30:00', 1329.98, 'delivered', '123 Main St, New York, NY 10001'),
(2, '2024-01-16 14:20:00', 79.99, 'shipped', '456 Oak Ave, Los Angeles, CA 90001'),
(3, '2024-01-17 09:15:00', 489.98, 'pending', '789 Pine Rd, Chicago, IL 60601'),
(1, '2024-01-18 11:45:00', 29.99, 'delivered', '123 Main St, New York, NY 10001'),
(4, '2024-01-19 16:30:00', 199.99, 'shipped', '321 Elm St, San Francisco, CA 94102'),
(5, '2024-01-20 08:00:00', 399.99, 'delivered', '654 Maple Dr, Boston, MA 02101'),
(6, '2024-01-21 13:20:00', 49.99, 'delivered', '987 Cedar Ln, Seattle, WA 98101'),
(7, '2024-01-22 10:10:00', 12.99, 'pending', '147 Birch Way, Austin, TX 78701'),
(8, '2024-01-23 15:45:00', 349.99, 'shipped', '258 Spruce Ct, Denver, CO 80201'),
(9, '2024-01-24 12:30:00', 24.99, 'delivered', '369 Willow St, Portland, OR 97201'),
(10, '2024-01-25 09:00:00', 89.99, 'delivered', '741 Ash Ave, Miami, FL 33101'),
(2, '2024-01-26 14:15:00', 1299.99, 'pending', '456 Oak Ave, Los Angeles, CA 90001');

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 1, 1299.99, 1299.99),
(1, 2, 1, 29.99, 29.99),
(2, 5, 1, 79.99, 79.99),
(3, 4, 1, 399.99, 399.99),
(3, 2, 3, 29.99, 89.99),
(4, 2, 1, 29.99, 29.99),
(5, 7, 1, 199.99, 199.99),
(6, 4, 1, 399.99, 399.99),
(7, 6, 1, 49.99, 49.99),
(8, 9, 1, 12.99, 12.99),
(9, 8, 1, 349.99, 349.99),
(10, 10, 1, 24.99, 24.99),
(11, 3, 1, 89.99, 89.99),
(12, 1, 1, 1299.99, 1299.99);

-- Insert reviews
INSERT INTO reviews (product_id, user_id, rating, comment, created_at) VALUES
(1, 1, 5, 'Excellent laptop, very fast and reliable!', '2024-01-20 10:00:00'),
(2, 1, 4, 'Good mouse, comfortable to use.', '2024-01-20 10:05:00'),
(5, 2, 5, 'Great coffee maker, makes perfect coffee every morning.', '2024-01-22 08:00:00'),
(4, 5, 5, 'Amazing 4K display, colors are vibrant!', '2024-01-25 14:00:00'),
(6, 6, 4, 'Good sound quality for the price.', '2024-01-26 11:00:00'),
(7, 4, 5, 'Very comfortable chair, helps with back pain.', '2024-01-27 09:00:00'),
(3, 10, 4, 'Nice keyboard, typing feels great.', '2024-01-28 16:00:00'),
(8, 8, 5, 'Love the standing desk, very sturdy.', '2024-01-29 10:00:00'),
(9, 7, 3, 'Decent notebooks, paper quality could be better.', '2024-01-30 12:00:00'),
(10, 9, 4, 'Nice pen set, good value for money.', '2024-01-31 15:00:00');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Display summary
SELECT 'Sample data loaded successfully!' AS message;
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_products FROM products;
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS total_reviews FROM reviews;

