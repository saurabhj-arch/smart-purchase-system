from django.contrib import admin
from .models import Product, Website, Price

admin.site.register(Product)
admin.site.register(Website)
admin.site.register(Price)