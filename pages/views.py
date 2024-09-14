from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from accounts.forms import CustomUserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q

from devices.models import (
    Product,
    Request,
    Stock,
    Facility,
    Category,  # Importing the Category model
)


def is_superuser(user):
    return user.is_superuser


### Admin View: Manage Requests
@login_required
@user_passes_test(is_superuser)
def manage_requests(request):
    # Fetch all pending requests (both new and return requests)
    all_requests = Request.objects.filter(status="pending").order_by("-id")

    if request.method == "POST":
        action = request.POST.get("action")
        request_id = request.POST.get("request_id")
        req = Request.objects.get(id=request_id)

        # Check if the request is of type 'new'
        if req.request_type == "new":
            if action == "accept":
                req.status = "approved"
                req.save()
            elif action == "deny":
                req.status = "denied"
                req.save()
                # Revert stock if denied
                stock = Stock.objects.get(product=req.product)
                stock.quantity += req.quantity
                stock.save()

        # Check if the request is of type 'return'
        elif req.request_type == "return":
            if action == "accept":
                # Accepting the return request should increase the stock
                stock = Stock.objects.get(product=req.product)
                stock.quantity += req.quantity
                stock.save()

                # Mark the return request as approved
                req.status = "returned"
                req.save()

        return redirect("manage_requests")

    return render(request, "admin/manage_requests.html", {"requests": all_requests})


@login_required
def submit_return_request(request, request_id):
    if request.method == "POST":
        try:
            # Fetch the specific request using the provided request_id
            user_request = Request.objects.get(
                id=request_id, user=request.user, status="approved"
            )
        except Request.DoesNotExist:
            messages.error(
                request, "عذراً، الطلب المقبول غير موجود.", extra_tags="alert-danger"
            )
            return redirect("home")

        # Update the request to become a return request
        user_request.request_type = "return"
        user_request.status = "pending"
        user_request.save()

        messages.success(
            request, "تم تقديم طلب الإرجاع بنجاح.", extra_tags="alert-success"
        )

    return redirect("about")


### View: Submit Request
@login_required
def submit_request(request):
    if request.method == "POST":
        if request.user.is_superuser:
            messages.error(request, "المدراء لا يمكنهم طلب المنتجات!")
            return redirect("home")

        category_id = request.POST.get("category")
        facility_id = request.POST.get("facility")
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(
                request, "عذراً، المنتج غير موجود.", extra_tags="alert-danger"
            )
            return redirect("home")

        stock, created = Stock.objects.get_or_create(
            product=product, defaults={"quantity": 0}
        )

        if created or stock.quantity < quantity:
            messages.error(
                request,
                "عذراً، لا يوجد مخزون كافي لهذا المنتج.",
                extra_tags="alert-danger",
            )
        else:
            stock.quantity -= quantity
            stock.save()
            # Mark the request as a "new" type by default
            Request.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                request_type="new",
            )
            messages.success(
                request, "تم طلبك بنجاح، طلبك في الطريق!", extra_tags="alert-success"
            )

        # Redirect back to the home page with filters applied
        return redirect(
            f"{reverse('home')}?facility={facility_id}&category={category_id}"
        )

    return redirect("home")


### View: Cancel Request
@require_POST
@login_required
def cancel_request(request, request_id):
    try:
        user_request = Request.objects.get(id=request_id, user=request.user)
        # Increment stock quantity only for 'new' requests (not return)
        if user_request.request_type == "new":
            stock = Stock.objects.get(product=user_request.product)
            stock.quantity += user_request.quantity
            stock.save()

        # Delete the request or mark as cancelled
        user_request.delete()
        messages.success(request, "تمت العملية بنجاح.", extra_tags="alert-success")
    except Request.DoesNotExist:
        messages.error(request, "لم يتم العثور على الطلب.", extra_tags="alert-danger")
    except Stock.DoesNotExist:
        messages.error(request, "خطأ في تحديث المخزون.", extra_tags="alert-danger")

    return redirect("about")


### View: Home Page
@login_required(login_url="/accounts/login/")
def home(request):
    facility_id = request.GET.get("facility", None)
    category_id = request.GET.get("category", None)
    query = request.GET.get("q", None)

    facilities = Facility.objects.all()  # Fetch all facilities
    products = Product.objects.all()

    # Filter products by facility
    if facility_id:
        try:
            selected_facility = Facility.objects.get(id=facility_id)
            products = products.filter(facility=selected_facility)
        except Facility.DoesNotExist:
            selected_facility = None
    else:
        selected_facility = None

    # Get distinct categories from the products in the selected facility
    categories = Category.objects.filter(product__in=products).distinct()

    # Filter products by category
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            products = products.filter(category=selected_category)
        except Category.DoesNotExist:
            selected_category = None
    else:
        selected_category = None

    # Filter products by search query
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(model__icontains=query)
            | Q(manufacturer__icontains=query)
        )

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "pages/home.html",
        {
            "page_obj": page_obj,
            "facilities": facilities,
            "selected_facility": selected_facility,
            "categories": categories,
            "selected_category": selected_category,
            "search_query": query,
        },
    )


### View: About Page
class AboutPageView(TemplateView):
    template_name = "pages/about.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_requests = Request.objects.filter(user=request.user).order_by(
            "-request_date"
        )
        return render(request, self.template_name, {"user_requests": user_requests})


### View: Profile
@login_required
def profile_view(request):
    if request.method == "POST":
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
                update_session_auth_hash(request, user)
                messages.success(request, "تم تغيير كلمة المرور بنجاح.")
                return redirect("profile")
            else:
                messages.error(request, "من فضلك تأكد من صحة البيانات.")
    else:
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


### Profile Page View
class ProfilePageView(TemplateView):
    template_name = "pages/profile.html"


class HomePageView(TemplateView):
    template_name = "pages/home.html"
