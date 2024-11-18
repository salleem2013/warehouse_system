```bash
# إنشاء بيئة افتراضية جديدة باستخدام Python

$ python -m venv .venv

# تفعيل البيئة الافتراضية في نظام ويندوز
# أولاً: تعيين سياسة التنفيذ للسماح بتشغيل السكربتات
$ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# ثانياً: تفعيل البيئة الافتراضية
$ .venv\Scripts\Activate.ps1
 
# تفعيل البيئة الافتراضية في نظام ماك ولينكس
$ source .venv/bin/activate

# خطوات إعداد المشروع داخل البيئة الافتراضية
# تثبيت جميع المكتبات المطلوبة من ملف requirements.txt
(.venv) $ pip install -r requirements.txt

# تطبيق الترحيلات على قاعدة البيانات
(.venv) $ python manage.py migrate

# إنشاء حساب المشرف (المدير)
(.venv) $ python manage.py createsuperuser

# تشغيل خادم التطوير المحلي
(.venv) $ python manage.py runserver
# بعد تشغيل الخادم، يمكن الوصول للموقع من خلال المتصفح على العنوان التالي
# فتح الموقع على الرابط http://127.0.0.1:8000
------------------------------------------------------------------------

# طريقة تشغيل المشروع باستخدام دوكر
# بناء وتشغيل الحاويات في الخلفية
$ docker-compose up -d --build

# تطبيق الترحيلات على قاعدة البيانات داخل حاوية الويب
$ docker-compose exec web python manage.py migrate

# إنشاء حساب المشرف داخل حاوية الويب
$ docker-compose exec web python manage.py createsuperuser

# بعد اكتمال الإعداد، يمكن الوصول للموقع من خلال المتصفح على العنوان التالي
# فتح الموقع على الرابط http://127.0.0.1:8001
```
# لتثبيت دوكر على ويندوز ماك او لينكس يمكن اتباع الخطوات التالية
# https://docs.docker.com/desktop/install/windows-install/
# https://docs.docker.com/desktop/install/mac-install/
# https://docs.docker.com/desktop/install/linux/