
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm
from saas_app.core.models import Tier
from saas_app.accounts.models import CustomUser, Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login


def signup(request, tier_id):
    tier = get_object_or_404(Tier, id=tier_id)

    # Check if tier has reached max users
    current_count = Profile.objects.filter(tier=tier).count()
    if tier.max_users is not None and current_count >= tier.max_users:
        return render(request, "accounts/signup_limit.html", {"tier": tier})

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create user (adjust if using custom fields)
            user = CustomUser.objects.create_user(
                username=form.cleaned_data["username"],  # or email if your form uses it
                password=form.cleaned_data["password1"]
            )
            # Assign tier to profile
            user.profile.tier = tier
            user.profile.save()

            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form, "tier": tier})
