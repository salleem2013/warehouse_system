from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from accounts.forms import CustomUserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from devices.models import (
    المنتجات,
    Request,
    المخزون,
)  # Importing the Product model from the devices app
from django.db.models import Q


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


@login_required(
    login_url="/accounts/login/"
)  # Redirect to the login page if not authenticated
def home(request):
    category = request.GET.get("category", None)
    query = request.GET.get("q", None)  # Get the search query

    # Filter products based on category or search query
    products = المنتجات.objects.all()

    if category:
        products = products.filter(الفئة=category)

    if query:
        # Use Q objects to search across multiple fields (name, description, model)
        products = products.filter(
            Q(الاسم__icontains=query)
            | Q(الوصف__icontains=query)
            | Q(الموديل__icontains=query)
            | Q(الصناعة__icontains=query)
        )

    paginator = Paginator(products, 12)  # Adjust number as needed
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/home.html",
        {
            "page_obj": page_obj,
            "current_category": category,  # Pass the current category to the template
            "search_query": query,  # Pass the search query back to the template
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


@login_required
def profile_view(request):
    if request.method == "POST":
        # Check if the form being submitted is the profile form or password form
        if "update_profile" in request.POST:
            profile_form = CustomUserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "تم تحديث معلوماتك الشخصية بنجاح.")
                return redirect("profile")
            else:
                messages.error(request, "خطأ في تحديث الملف الشخصي.")

        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, "تم تغيير كلمة المرور بنجاح.")
                return redirect("profile")
            else:
                messages.error(request, "من فضلك تأكد من صحة البيانات.")
    else:
        # GET method: provide both forms for display
        profile_form = CustomUserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(
        request,
        "pages/profile.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )
