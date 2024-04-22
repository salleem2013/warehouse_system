from django.contrib import admin
from .models import المنتجات, المخزون, Request

admin.site.register(المنتجات)
admin.site.register(المخزون)


class المنتجاتAdmin(admin.ModelAdmin):
    list_display = ["الاسم", "الموديل", "الفئة", "الصورة"]
