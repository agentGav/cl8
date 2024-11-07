from django import template
from django.contrib.auth import get_user_model
from ..models import Profile

register = template.Library()
User = get_user_model()

@register.filter
def custom_user_display(user):
    if not isinstance(user, User):
        return ''
    
    profile = Profile.objects.filter(user=user).first()
    if profile:
        return profile.name
    return f"{user.first_name} {user.last_name}"
