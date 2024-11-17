from dal import autocomplete
from django import forms
from django.contrib.auth import forms as auth_forms
from django.core.validators import URLValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _
from taggit import models as taggit_models

from .importers import safe_username
from .models import Profile, User

User = get_user_model()


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta(auth_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(auth_forms.UserCreationForm):
    error_message = auth_forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(auth_forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class ProfileUpdateForm(forms.ModelForm):
    name = forms.CharField()
    email = forms.EmailField()

    tags = ModelMultipleChoiceField(
        queryset=taggit_models.Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="tag-autocomplete-with-create"),
        required=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        url_validator = URLValidator()
        social_fields = ["website", "social_1", "social_2", "social_3"]

        # Loop through the social fields and validate each one
        for field in social_fields:
            social_link = cleaned_data.get(field)
            if social_link:  # Only validate if the field is not empty
                try:
                    url_validator(social_link)
                except ValidationError:
                    self.add_error(field, "Please enter a valid URL for this social link.")

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        # Update user's name
        self.instance.user.name = self.cleaned_data.get("name")
        
        # Update user's email
        self.instance.user.email = self.cleaned_data.get("email")

        # Save user instance
        if commit:
            self.instance.user.save()

        return super().save(commit=commit)

    class Meta:
        model = Profile
        fields = [
            "photo",
            "email",
            "name",
            "phone",
            "website",
            "location",
            "organisation",
            "bio",
            "tags",
            "social_1",
            "social_2",
            "social_3",
            "visible",
        ]


class ProfileCreateForm(forms.ModelForm):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    tags = ModelMultipleChoiceField(
        queryset=taggit_models.Tag.objects.all(),
        required=False,  # Set required to False
        widget=autocomplete.ModelSelect2Multiple(url="tag-autocomplete-with-create"),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        url_validator = URLValidator()
        social_fields = ["website", "social_1", "social_2", "social_3"]

        # Loop through the social fields and validate each one
        for field in social_fields:
            social_link = cleaned_data.get(field)
            if social_link:  # Only validate if the field is not empty
                try:
                    url_validator(social_link)
                except ValidationError:
                    self.add_error(field, "Please enter a valid URL for this social link.")

        return cleaned_data

    def save(self, commit=True):
        """
        Create a user, then save the corresponding profile object
        """

        email = self.cleaned_data.get("email")
        user, created = User.objects.get_or_create(
            email=email,
        )
        user.username = safe_username()
        user.name = self.cleaned_data.get("name")
        user.save(), 
        profile, profile_create = Profile.objects.get_or_create(user=user)

        profile.phone = self.cleaned_data.get("phone")
        profile.website = self.cleaned_data.get("website")
        profile.social_1 = self.cleaned_data.get("social_1")
        profile.social_2 = self.cleaned_data.get("social_2")
        profile.social_3 = self.cleaned_data.get("social_3")
        profile.bio = self.cleaned_data.get("bio")
        profile.visible = self.cleaned_data.get("visible")
        profile.short_id = safe_username()
        profile.import_id = "profile-form"
        profile.photo = self.cleaned_data.get("photo")

        profile.save()
        profile.update_thumbnail_urls()

        self.instance = profile
        result = super().save(commit=commit)

        # add the user to the 'member' group
        member_group = Group.objects.get(name="member")
        member_group.user_set.add(user)
        member_group.save()

        return result

    class Meta:
        model = Profile
        fields = [
            "photo",
            "name",
            "email",
            "location",
            "website",
            "organisation",
            "bio",
            "phone",
            "tags",
            "social_1",
            "social_2",
            "social_3",
            "visible",
        ]
