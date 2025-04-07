from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, URLValidator

class Product(models.Model):
    name = models.CharField(max_length=1500, help_text="Product name from Amazon")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        help_text="Product price in USD"
    )
    rating = models.CharField(
        max_length=10, 
        help_text="Product rating (e.g., '4.5')",
        default="N/A"
    )
    review_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of product reviews",
        default=0
    )
    url = models.URLField(
        max_length=500,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text="Amazon product URL"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def to_dict(self):
        """Convert model instance to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'rating': self.rating,
            'review_count': self.review_count,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['price']),
        ]

class Seller(models.Model):
    name = models.CharField(
        max_length=500, 
        help_text="Name of ecommerce website")

    url = models.URLField(
        max_length=500,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text="Amazon product URL"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        """Convert model instance to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    class Meta:
        ordering = ['-created_at']

class Platform(models.Model):
    name = models.CharField(
        max_length=500, 
        help_text="Name of ecommerce website")

    url = models.URLField(
        max_length=500,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text="Amazon product URL"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        """Convert model instance to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    class Meta:
        ordering = ['-created_at']

