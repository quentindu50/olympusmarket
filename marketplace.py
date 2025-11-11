"""
Simple marketplace module for OlympusMarket.
This module provides basic marketplace functionality for managing products.
"""


class Product:
    """Represents a product in the marketplace."""
    
    def __init__(self, name, price, description=""):
        """
        Initialize a product.
        
        Args:
            name (str): Product name
            price (float): Product price
            description (str): Product description
        """
        self.name = name
        self.price = price
        self.description = description
    
    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"


class Marketplace:
    """Manages products in the marketplace."""
    
    def __init__(self):
        """Initialize an empty marketplace."""
        self.products = []
    
    def add_product(self, product):
        """
        Add a product to the marketplace.
        
        Args:
            product (Product): Product to add
        """
        self.products.append(product)
    
    def get_products(self):
        """
        Get all products in the marketplace.
        
        Returns:
            list: List of products
        """
        return self.products
    
    def find_product_by_name(self, name):
        """
        Find a product by name.
        
        Args:
            name (str): Product name to search for
            
        Returns:
            Product or None: Found product or None
        """
        for product in self.products:
            if product.name == name:
                return product
        return None
