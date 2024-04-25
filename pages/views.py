from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from devices.models import (
    المنتجات,
    Request,
    المخزون,
)  # Importing the Product model from the devices app


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def manage_requests(request):
    all_requests = Request.objects.filter(status="pending").order_by("-id")
    if request.method == "POST":
        action = request.POST.get("action")
        request_id = request.POST.get("request_id")
        req = Request.objects.get(id=request_id)

        if action == "accept":
            req.status = "accepted"
            req.save()
        elif action == "deny":
            req.status = "denied"
            req.save()
            # Revert stock if denied
            inventory = المخزون.objects.get(المنتجات=req.product)
            inventory.الكمية += req.quantity
            inventory.save()

        return redirect("manage_requests")

    return render(request, "admin/manage_requests.html", {"requests": all_requests})


@login_required
def submit_request(request):
    if request.method == "POST":
        if request.user.is_superuser:
            messages.error(request, "المدراء لا يمكنهم طلب المنتجات!")
            return redirect("home")
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        try:
            product = المنتجات.objects.get(id=product_id)
        except المنتجات.DoesNotExist:
            messages.error(
                request, "عذراً، المنتج غير موجود.", extra_tags="alert-danger"
            )
            return redirect("home")

        inventory, created = المخزون.objects.get_or_create(
            المنتجات=product, defaults={"الكمية": 0}
        )

        if created or inventory.الكمية < quantity:
            messages.error(
                request,
                "عذراً، لا يوجد مخزون كافي لهذا المنتج.",
                extra_tags="alert-danger",
            )
        else:
            inventory.الكمية -= quantity
            inventory.save()
            Request.objects.create(
                user=request.user, product=product, quantity=quantity
            )
            messages.success(
                request, "تم طلبك بنجاح، طلبك في الطريق!", extra_tags="alert-success"
            )

        return redirect("home")
    return redirect("home")


@require_POST
@login_required
def cancel_request(request, request_id):
    try:
        user_request = Request.objects.get(id=request_id, user=request.user)
        # Increment stock quantity
        inventory = المخزون.objects.get(المنتجات=user_request.product)
        inventory.الكمية += user_request.quantity
        inventory.save()
        # Delete the request or mark as cancelled
        user_request.delete()  # Or update if you wish to keep record
        messages.success(request, "تمت العملية بنجاح.", extra_tags="alert-success")
    except Request.DoesNotExist:
        messages.error(request, "لم يتم العثور على الطلب.", extra_tags="alert-danger")
    except المخزون.DoesNotExist:
        messages.error(request, "خطأ في تحديث المخزون.", extra_tags="alert-danger")

    return redirect("about")


from django.core.paginator import Paginator
from django.shortcuts import render


def home(request):
    category = request.GET.get("category", None)
    if category:
        products = المنتجات.objects.filter(الفئة=category).prefetch_related(
            "المخزون_set"
        )
    else:
        products = المنتجات.objects.all().prefetch_related("المخزون_set")

    paginator = Paginator(products, 12)  # Adjust number as needed
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/home.html",
        {
            "page_obj": page_obj,
            "current_category": category,  # Pass the current category to the template
        },
    )


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Fetch all requests made by the current logged-in user
        user_requests = Request.objects.filter(user=request.user).order_by(
            "-request_date"
        )
        return render(request, self.template_name, {"user_requests": user_requests})


class ProfilePageView(TemplateView):
    template_name = "pages/profile.html"
