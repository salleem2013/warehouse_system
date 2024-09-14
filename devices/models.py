from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Facility(models.Model):
    """Represents different facilities such as Electronics, Networking, etc."""

    name = models.CharField(_("Facility Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Facility")
        verbose_name_plural = _("Facilities")


class Category(models.Model):
    """Represents product categories."""

    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Product(models.Model):
    """Represents products which can belong to different categories."""

    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, default=1, verbose_name=_("Facility")
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, verbose_name=_("Category")
    )
    name = models.CharField(_("Product Name"), max_length=255)
    image = models.ImageField(
        _("Image"), upload_to="product_images/", blank=True, null=True
    )
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)
    model = models.CharField(_("Model"), max_length=255)
    serial_number = models.CharField(_("Serial Number"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.model} - {self.manufacturer} - {self.facility} ({self.serial_number})"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class Stock(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    quantity = models.IntegerField(_("Quantity"), default=0, null=False)

    def __str__(self):
        return f"عدد {self.quantity} {self.product.name} - {self.product.model} - {self.product.manufacturer} - {self.product.facility}"

    class Meta:
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")


class Request(models.Model):
    REQUEST_TYPE_CHOICES = [
        ("new", _("New Request")),
        ("return", _("Return Request")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    quantity = models.IntegerField(_("Quantity"), default=1)
    request_date = models.DateField(_("Request Date"), auto_now_add=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        default="pending",
        choices=[
            ("pending", _("Pending")),
            ("approved", _("Approved")),
            ("denied", _("Denied")),
            ("returned", _("Returned")),
        ],
    )
    request_type = models.CharField(
        _("Request Type"), max_length=20, choices=REQUEST_TYPE_CHOICES, default="new"
    )

    def __str__(self):
        return f"Request by {self.user.username} for {self.quantity} x {self.product.name} ({self.status})"
