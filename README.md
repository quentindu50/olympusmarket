# OlympusMarket

A simple marketplace application built with Python.

## Features

- Product management
- Simple marketplace operations
- Easy to extend and customize

## Getting Started

### Running Tests

```bash
python test_marketplace.py
```

## Project Structure

- `marketplace.py` - Core marketplace functionality
- `test_marketplace.py` - Unit tests for the marketplace

## Usage Example

```python
from marketplace import Product, Marketplace

# Create a marketplace
market = Marketplace()

# Add products
product1 = Product("Laptop", 999.99, "High-performance laptop")
product2 = Product("Mouse", 29.99, "Wireless mouse")

market.add_product(product1)
market.add_product(product2)

# Get all products
products = market.get_products()
for product in products:
    print(product)
```
