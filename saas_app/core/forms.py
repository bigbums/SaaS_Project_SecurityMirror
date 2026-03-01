from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Tenant, TenantUser, Tier
from saas_app.accounts.models import CustomUser



# -----------------------------
# Bootstrap Mixin
# -----------------------------
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


# -----------------------------
# Signup Form
# -----------------------------


# -----------------------------
# Login Form
# -----------------------------
class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(label="Email")


# -----------------------------
# Tenant Form
# -----------------------------
class TenantForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ["name", "email", "tier", "status"]



# -----------------------------
# Subscription/signup Form
# -----------------------------



class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    subscription_plan = forms.ModelChoiceField(
        queryset=Tier.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2", "company_name", "subscription_plan"]



# -----------------------------
# TenantUser Form
# -----------------------------
class TenantUserForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TenantUser
        fields = ["tenant", "user", "role"]
