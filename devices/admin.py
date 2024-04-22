from django.contrib import admin
from .models import المنتجات, المخزون, Request

admin.site.register(المنتجات)
admin.site.register(المخزون)
admin.site.register(Request)


class المنتجاتAdmin(admin.ModelAdmin):
    list_display = ["الاسم", "الموديل", "الفئة", "الصورة"]
