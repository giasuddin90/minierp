from django.contrib.auth.views import LoginView
from django.urls import path
from django.contrib import admin

class CustomAdminLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

# Override the admin login view
admin.site.login = CustomAdminLoginView.as_view()
