from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpRequest
from django.shortcuts import redirect


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        A hook to catch a a social sign in, and match it to the corresponding
        user who has already been imported
        """

        from backend.users.models import User

        if "email" not in sociallogin.account.extra_data:
            return

        try:
            email = sociallogin.account.extra_data.get("email")
            user = User.objects.get(email__iexact=email.lower())

        # if it does not, let allauth take care of this new social account
        except User.DoesNotExist:
            return

        # short circuit
        # we log the user in here without finishing the
        # rest of the allauth flow.
        # This is bad, but if we continue we get a 500 when an assertion
        # fails at `self.is_existing` when calling `sociallogin.connect`
        backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user, backend=backend)

        # exit the flow to go back to the home page, and let vue
        # take over
        raise ImmediateHttpResponse(redirect("home"))
        #
        # sociallogin.connect(request, user)

    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

