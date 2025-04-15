from django.db import models
from scrape.models import Product

# Create your models here.

class ProductSnapshot(models.Model):
    product = models.ForeignKey('scrape.Product', on_delete=models.CASCADE)
    price = models.FloatField() 
    rating = models.FloatField()  
    reviews_count = models.IntegerField(null=True, blank=True)
    delta_price = models.FloatField(null=True)
    delta_rating = models.CharField(null = True, max_length=10, default="0", help_text="Rating difference from previous snapshot")
    delta_review_count = models.IntegerField(null = True, default=0, help_text="Review count difference from previous snapshot")
    captured_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when snapshot was taken")

    def __str__(self):
        return f"Snapshot of {self.product.name} on {self.captured_at}"

    def save(self, *args, **kwargs):
        """Override save to calculate deltas before saving"""
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["-captured_at"]),
            models.Index(fields=["product"]),
        ]


class SEOKeywordTracking(models.Model):
    product_id = models.ForeignKey('scrape.product', on_delete=models.CASCADE, null=False, default=0)
    product_name = models.CharField(max_length=255)
    product_url = models.URLField()
    top_seo_keywords = models.JSONField(default=list)  # Storing keywords as a list
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} - Keywords Tracked"

    class Meta:
        indexes = [
            models.Index(fields=["product_name"]),
            models.Index(fields=["created_at"])
        ]