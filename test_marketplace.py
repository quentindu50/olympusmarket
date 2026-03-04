"""
Tests for the marketplace module.
"""
import unittest
from marketplace import Product, Marketplace


class TestProduct(unittest.TestCase):
    """Test cases for Product class."""
    
    def test_product_creation(self):
        """Test creating a product."""
        product = Product("Test Item", 19.99, "A test product")
        self.assertEqual(product.name, "Test Item")
        self.assertEqual(product.price, 19.99)
        self.assertEqual(product.description, "A test product")
    
    def test_product_str(self):
        """Test product string representation."""
        product = Product("Widget", 25.50)
        self.assertEqual(str(product), "Widget - $25.50")


class TestMarketplace(unittest.TestCase):
    """Test cases for Marketplace class."""
    
    def setUp(self):
        """Set up test marketplace."""
        self.marketplace = Marketplace()
    
    def test_marketplace_init(self):
        """Test marketplace initialization."""
        self.assertEqual(len(self.marketplace.products), 0)
    
    def test_add_product(self):
        """Test adding a product to marketplace."""
        product = Product("Gadget", 49.99)
        self.marketplace.add_product(product)
        self.assertEqual(len(self.marketplace.products), 1)
        self.assertEqual(self.marketplace.products[0], product)
    
    def test_get_products(self):
        """Test getting all products."""
        product1 = Product("Item 1", 10.00)
        product2 = Product("Item 2", 20.00)
        self.marketplace.add_product(product1)
        self.marketplace.add_product(product2)
        products = self.marketplace.get_products()
        self.assertEqual(len(products), 2)
        self.assertIn(product1, products)
        self.assertIn(product2, products)
    
    def test_find_product_by_name(self):
        """Test finding a product by name."""
        product = Product("Special Item", 99.99)
        self.marketplace.add_product(product)
        found = self.marketplace.find_product_by_name("Special Item")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Special Item")
    
    def test_find_nonexistent_product(self):
        """Test finding a product that doesn't exist."""
        found = self.marketplace.find_product_by_name("Nonexistent")
        self.assertIsNone(found)


if __name__ == '__main__':
    unittest.main()
