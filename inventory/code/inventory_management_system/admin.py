from django.contrib import admin
from .models import Parts, Building, Location, Inventory_details, Move_log, Product_rate, Purchase
# Register your models here.

admin.site.register(Parts)
admin.site.register(Building)
admin.site.register(Location)
admin.site.register(Inventory_details)
admin.site.register(Move_log)
admin.site.register(Product_rate)
admin.site.register(Purchase)