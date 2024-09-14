from django.contrib import admin
from .models import Category, Facility, Product, Request, Stock


# admin.site.register(Request)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "facility",
        "manufacturer",
        "model",
        "description",
        "category",
        "serial_number",
    )
    search_fields = ("serial_number", "name", "model", "manufacturer", "description")
    list_filter = ("facility", "category")
    ordering = ("facility",)
    autocomplete_fields = ("facility", "category")
    list_per_page = 20


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity")
    search_fields = ("product",)
    autocomplete_fields = ("product",)
    list_per_page = 20


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    sortable_by = "name"
    list_per_page = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    list_per_page = 10


# @admin.register(Tire)
# class TireAdmin(admin.ModelAdmin):
#     list_display = ("title", "brand", "width", "ratio", "diameter", "available")
#     search_fields = ("title", "brand__name", "width", "ratio", "diameter")
#     list_filter = ("brand", "available")
#     ordering = ("title",)
#     readonly_fields = (
#         "store_moving_price",
#         "spare_moving_price",
#         "delivery_moving_price",
#     )
