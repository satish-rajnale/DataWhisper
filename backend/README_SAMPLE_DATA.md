# Sample Database Setup

This document explains how to set up sample data in the database for testing the Natural Language SQL Chat application.

## Quick Start

### Using Docker Compose

1. Start the PostgreSQL container:
```bash
docker-compose up -d postgres
```

2. Copy the SQL script into the container:
```bash
docker-compose cp backend/init_sample_data.sql valid-query-postgres:/tmp/init_sample_data.sql
```

3. Execute the script:
```bash
docker-compose exec postgres psql -U postgres -d validquery -f /tmp/init_sample_data.sql
```

### Using Local PostgreSQL

If you're running PostgreSQL locally:

```bash
psql -U postgres -d validquery -f backend/init_sample_data.sql
```

Or connect to psql and run the script:

```bash
psql -U postgres -d validquery
\i backend/init_sample_data.sql
```

## Sample Data Overview

The script creates the following tables with sample data:

### Tables Created

1. **users** (10 records)
   - id, name, email, age, city, created_at, is_active
   - Sample users from different cities

2. **products** (10 records)
   - id, name, category, price, stock_quantity, description
   - Electronics, Appliances, Furniture, Office Supplies

3. **orders** (12 records)
   - id, user_id, order_date, total_amount, status, shipping_address
   - Various statuses: pending, shipped, delivered

4. **order_items** (14 records)
   - id, order_id, product_id, quantity, unit_price, subtotal
   - Links orders to products

5. **reviews** (10 records)
   - id, product_id, user_id, rating, comment, created_at
   - Product reviews with 1-5 star ratings

### Relationships

- `orders.user_id` → `users.id` (Foreign Key)
- `order_items.order_id` → `orders.id` (Foreign Key)
- `order_items.product_id` → `products.id` (Foreign Key)
- `reviews.product_id` → `products.id` (Foreign Key)
- `reviews.user_id` → `users.id` (Foreign Key)

## Example Queries to Try

Once the sample data is loaded, try asking these questions:

1. "How many users do we have?"
2. "Show me all products in the Electronics category"
3. "What are the top 5 products by price?"
4. "How many orders are pending?"
5. "Show me all orders for user John Doe"
6. "What is the average rating for products?"
7. "Which products have the most reviews?"
8. "Show me all users from New York"
9. "What is the total revenue from all orders?"
10. "Which products are out of stock?"

## Verifying Data

After running the script, verify the data was loaded:

```sql
SELECT COUNT(*) FROM users;      -- Should return 10
SELECT COUNT(*) FROM products;   -- Should return 10
SELECT COUNT(*) FROM orders;     -- Should return 12
SELECT COUNT(*) FROM order_items; -- Should return 14
SELECT COUNT(*) FROM reviews;    -- Should return 10
```

## Resetting Data

To reset and reload the sample data:

```bash
# Drop and recreate tables (WARNING: This deletes all data)
docker-compose exec postgres psql -U postgres -d validquery -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Then run the init script again
docker-compose exec postgres psql -U postgres -d validquery -f /tmp/init_sample_data.sql
```

## Notes

- All tables include comments explaining each column
- Foreign key constraints ensure data integrity
- Indexes are created for better query performance
- The script is idempotent (safe to run multiple times with `CREATE TABLE IF NOT EXISTS`)

