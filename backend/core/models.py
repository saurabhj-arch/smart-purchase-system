from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Website(models.Model):
    name = models.CharField(max_length=100)
    base_url = models.URLField()

    def __str__(self):
        return self.name
    

class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_url = models.URLField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'website')
    
