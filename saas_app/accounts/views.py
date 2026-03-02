
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from saas_app.core.models import Tier
from saas_app.accounts.models import CustomUser, Profile


def signup(request, tier_id):
    tier = get_object_or_404(Tier, id=tier_id)

    # Count how many users already belong to this tier
    current_count = Profile.objects.filter(tier=tier).count()
    if tier.max_users is not None and current_count >= tier.max_users:
        return render(request, "accounts/signup_limit.html", {"tier": tier})

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                email=form.cleaned_data["email"],  # adjust if using email field
                password=form.cleaned_data["password1"]
            )
            user.profile.tier = tier
            user.profile.save()

            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form, "tier": tier})
