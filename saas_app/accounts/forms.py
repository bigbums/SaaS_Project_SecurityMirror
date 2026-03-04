from django import forms
from saas_app.accounts.models import CustomUser
from saas_app.core.models import Tenant, TenantUser, Tier

from django import forms
from django.core.exceptions import ValidationError
from saas_app.accounts.models import CustomUser
from saas_app.core.models import Tenant, TenantUser, Tier

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    company_name = forms.CharField(label="Company Name")
    tier_id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords don't match")
        return p2

    def clean_tier_id(self):
        tier_id = self.cleaned_data.get("tier_id")
        if not Tier.objects.filter(id=tier_id).exists():
            raise ValidationError("Invalid subscription tier")
        return tier_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

            # Create tenant linked to chosen tier
            tier = Tier.objects.get(id=self.cleaned_data["tier_id"])
            tenant = Tenant.objects.create(
                name=self.cleaned_data["company_name"],
                email=user.email,
                tier=tier,
                status="active"
            )

            # Link user to tenant as owner
            TenantUser.objects.create(user=user, tenant=tenant, role="owner")

        return user
