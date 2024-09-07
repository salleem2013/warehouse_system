from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class المنتجات(models.Model):
    CATEGORY_CHOICES = [
        ("laptop", "لابتوب"),
        ("desktop", "ديسكتوب"),
        ("server", "سيرفر"),
        ("accessory", "ملحقات"),
    ]
    الاسم = models.CharField(max_length=255)
    الصورة = models.ImageField(
        _("Image"), upload_to="product_images/", blank=True, null=True
    )
    الفئة = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="لابتوب")
    الصناعة = models.CharField(max_length=255)
    الموديل = models.CharField(max_length=255)
    الرقم_المتسلسل = models.CharField(max_length=100, unique=True)
    الوصف = models.TextField()

    def __str__(self):
        return f"{self.الاسم} - {self.الموديل} (الرقم التسلسلي: {self.الرقم_المتسلسل})"
    
    class Meta:
        verbose_name = _("المنتج")
        verbose_name_plural = _("المنتجات")
    


class المخزون(models.Model):
    المنتجات = models.OneToOneField(المنتجات, on_delete=models.CASCADE)
    الكمية = models.IntegerField(default=0, null=False)

    def __str__(self):
        return f"{self.الكمية} منتح من {self.المنتجات.الاسم} - {self.المنتجات.الموديل}"
    
    class Meta:
        verbose_name = _("مخزون")
        verbose_name_plural = _("المخزون")


class Request(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(المنتجات, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "قيد الانتظار"),
            ("approved", "موافق عليه"),
            ("denied", "مرفوض"),
        ],
    )

    def __str__(self):
        return f"Request by {self.user.username} for {self.quantity} x {self.product.الاسم} ({self.status})"
