from django.shortcuts import render
from pages.models import products


def home(request):
    product = products.objects.all()  # Retrieves all books from the database
    return render(request, "pages/home.html", {"products": product})
