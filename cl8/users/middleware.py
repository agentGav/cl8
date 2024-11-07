from .models import Constellation

class ConstellationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        try:
            request.constellation = Constellation.objects.get(site=request.site)
        except Exception as e:
            request.constellation = None

        response = self.get_response(request)
        
        

        # Code to be executed for each request/response after
        # the view is called.

        return response


from django.contrib.sites.shortcuts import get_current_site
from .models import Constellation, SendInviteEmailContent, PasswordResetEmailContent


class SiteConfigMiddleware:
    """
    Middleware to attach Constellation and SendInviteEmailContent objects
    to the request based on the current site.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Retrieve the current site for the request
        current_site = get_current_site(request)
        
        # Attach Constellation object to the request
        try:
            request.constellation = Constellation.objects.get(site=current_site)
        except Constellation.DoesNotExist:
            request.constellation = None
        
        # Attach SendInviteEmailContent object to the request
        try:
            request.email_confirmation = SendInviteEmailContent.objects.get(site=current_site)
        except SendInviteEmailContent.DoesNotExist:
            request.email_confirmation = None
            
        try:
            request.password_reset_content = PasswordResetEmailContent.objects.get(site=current_site)
        except PasswordResetEmailContent.DoesNotExist:
            request.password_reset_content = None

        # Call the next middleware or view
        response = self.get_response(request)

        return response