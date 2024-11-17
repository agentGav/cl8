import re
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import CharField
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from sorl.thumbnail import get_thumbnail
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase
from django.contrib.sites.models import Site
from shortuuid.django_fields import ShortUUIDField
import logging


logger = logging.getLogger(__name__)

# this is the string we use to identify an admin group
ADMIN_NAME = "admin"


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def has_profile(self) -> bool:
        """
        A convenience function to safely check if
        a user has a matching profile.
        """
        matching_profiles = Profile.objects.filter(user_id=self.id)
        if matching_profiles:
            return True

    def is_in_group(self, group_name: str) -> bool:
        """ """
        if self.groups.filter(name=group_name).exists():
            return True

        return False

    def is_admin(self) -> bool:
        """ """
        return self.is_in_group("admin")


class Cluster(TagBase):
    class Meta:
        verbose_name = _("Cluster")
        verbose_name_plural = _("Clusters")


class TaggedCluster(TaggedItemBase):
    content_object = models.ForeignKey("Profile", on_delete=models.CASCADE)

    tag = models.ForeignKey(
        Cluster,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


def flat_tag_list(tag_queryset) -> list[dict]:
    """
    Return a list of tags, with the name split on a colon to allow for grouping
    by the kind of tag listed.
    This is called multiple times, so we split on the name in python rather than
    going back to the database using further filters / exclude classes, which
    can cause N+1 queries
    """
    tag_list = []

    for tag in tag_queryset.all():
        split_name = tag.name.split(":")
        if len(split_name) == 1:
            # there was no colon to split on use the full tag name
            tag_list.append({"name": split_name[0], "tag": tag})
        if len(split_name) > 1:
            # we DO have a colon to split on - use the full tag name
            # and add the group, so we can use it for show the kinds
            # of tags as well
            tag_list.append({"group": split_name[0], "name": split_name[1], "tag": tag})

    return tag_list


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(_("phone"), max_length=254, blank=True, null=True)
    website = models.URLField(_("website"), max_length=200, blank=True, null=True)
    organisation = models.CharField(
        _("organisation"), max_length=254, blank=True, null=True
    )
    social_1 = models.CharField(_("social_1"), max_length=254, blank=True, null=True)
    social_2 = models.CharField(_("social_2"), max_length=254, blank=True, null=True)
    social_3 = models.CharField(_("social_3"), max_length=254, blank=True, null=True)
    bio = models.TextField(_("bio"), blank=True, null=True)
    visible = models.BooleanField(_("visible"), default=False)
    location = models.CharField(_("location"), max_length=254, blank=True, null=True)
    photo = models.ImageField(
        _("photo"), blank=True, null=True, max_length=200, upload_to="photos"
    )

    tags = TaggableManager(blank=True)
    clusters = TaggableManager("Clusters", blank=True, through=TaggedCluster)

    # short_id is a unique identifier for a profile, used in the URL
    short_id = ShortUUIDField(length=8, unique=True, blank=True, null=True)

    # for tracking where this profile was imported from
    import_id = models.CharField(
        _("import_code"), max_length=254, blank=True, null=True
    )
    # we have these as cache tables because when we use object storage
    # we end up making loads of requests to AWS just to return an url
    _photo_url = models.URLField(blank=True, null=True)
    _photo_thumbnail_url = models.URLField(blank=True, null=True)
    _photo_detail_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["user__name"]
        permissions = [
            ("set_visibility", "Can set the visibility of a profile"),
            ("send_invite_email", "Can send profile invite emails"),
            (
                "import_profiles",
                "Can import profiles from a CSV file, or from a Firebase export JSON file",
            ),
        ]

    @property
    def name(self):
        return self.user.name

    @name.setter
    def name(self, value):
        self.user.name = value

    @property
    def email(self):
        return self.user.email

    @property
    def admin(self):
        return self.user.is_staff

    @property
    def thumbnail_photo(self):
        if not self.photo:
            return None

        if self._photo_thumbnail_url:
            return self._photo_thumbnail_url

        return get_thumbnail(self.photo, "100x100", crop="center", quality=99).url

    @property
    def detail_photo(self):
        """
        A photo, designed for showing on a page, when viewing a profile,
        with a user's details

        """
        if not self.photo:
            return None

        if self._photo_detail_url:
            return self._photo_detail_url

        return get_thumbnail(self.photo, "250x250", crop="center", quality=99).url
    
    @property
    def social_1_name(self):
        """
        Extracts and returns the human-readable name of the website from the URL.
        For example, 'https://www.example.com/path?query=1' will return 'example'.
        """
        # Parse the URL to get the netloc (network location part)
        parsed_url = urlparse(self.social_1)
        domain = parsed_url.netloc

        # Remove the 'www.' prefix if present
        domain = domain.replace('www.', '')

        # Extract the base domain without subdomains and TLD
        match = re.match(r'^([^\.]+)\.', domain)
        name = match.group(1) if match else domain
        return name.capitalize()
    
    @property
    def social_2_name(self):
        """
        Extracts and returns the human-readable name of the website from the URL.
        For example, 'https://www.example.com/path?query=1' will return 'example'.
        """
        # Parse the URL to get the netloc (network location part)
        parsed_url = urlparse(self.social_2)
        domain = parsed_url.netloc

        # Remove the 'www.' prefix if present
        domain = domain.replace('www.', '')

        # Extract the base domain without subdomains and TLD
        match = re.match(r'^([^\.]+)\.', domain)
        name = match.group(1) if match else domain
        return name.capitalize()
    
    @property
    def social_3_name(self):
        """
        Extracts and returns the human-readable name of the website from the URL.
        For example, 'https://www.example.com/path?query=1' will return 'example'.
        """
        # Parse the URL to get the netloc (network location part)
        parsed_url = urlparse(self.social_3)
        domain = parsed_url.netloc

        # Remove the 'www.' prefix if present
        domain = domain.replace('www.', '')

        # Extract the base domain without subdomains and TLD
        match = re.match(r'^([^\.]+)\.', domain)
        name = match.group(1) if match else domain
        return name.capitalize()

    def tags_by_grouping(self):
        """
        Return a list of tags, grouped by their type
        """
        grouped_tags = {}
        ungrouped_tags = []
        # group tags in a dict based on the name of the tag, once it is split at the ":" in the name
        for tag in self.tags.filter(name__icontains=":").order_by("name"):
            try:
                tag_group, tag_name = tag.name.split(":")
                tag_name = tag.name.split(":")[1]
                if tag_group not in grouped_tags:
                    grouped_tags[tag_group] = []
                grouped_tags[tag_group].append({"name": tag_name, "tag": tag})
            except ValueError:
                logger.warning(f"Unable to split tag name: {tag.name}. Not showing.")

        for ungrouped_tag in self.tags.exclude(name__icontains=":").order_by("name"):
            ungrouped_tags.append({"name": ungrouped_tag.name, "tag": ungrouped_tag})

        return [grouped_tags, ungrouped_tags]

    def tags_with_no_grouping(self):
        """
        Return a list of tags, flattened into a single list
        """
        return flat_tag_list(self.tags)
        # tag_list = []
        # # group tags in a dict based on the name of the tag, once it is split at the ":" in the name
        # for tag in self.tags.filter(name__icontains=":"):
        #     tag_group, tag_name = tag.name.split(":")
        #     tag_list.append({"name": tag_name, "tag": tag})

        # for ungrouped_tag in self.tags.exclude(name__icontains=":"):
        #     tag_list.append({"name": ungrouped_tag.name, "tag": ungrouped_tag})

        # return tag_list

    def __str__(self):
        if self.user.name:
            return f"{self.user.name} - {self.import_id}"
        else:
            return f"{self.user.first_name} - {self.import_id}"

    def get_absolute_url(self):
        return reverse("profile-detail", args=[self.short_id])

    def update_thumbnail_urls(self):
        """Generate the thumbnails for a profile"""
        if self.photo:
            self._photo_url = self.photo.url
            self._photo_thumbnail_url = get_thumbnail(
                self.photo, "100x100", crop="center", quality=99
            ).url
            self._photo_detail_url = get_thumbnail(
                self.photo, "250x250", crop="center", quality=99
            ).url

            self.save(
                update_fields=[
                    "_photo_thumbnail_url",
                    "_photo_detail_url",
                    "_photo_url",
                ]
            )

    def get_context_for_emails(self) -> dict:
        current_site = Site.objects.get_current()
        constellation = Constellation.objects.get(site=current_site)
        email_confirmation = SendInviteEmailContent.objects.filter(site=current_site).first()
        support_email_address = settings.SUPPORT_EMAIL

        return {
            "profile": self,
            "support_email_address": support_email_address,
            "constellation": constellation,
            "site": current_site,
            "email_confirmation":email_confirmation,
        }

    def send_invite_mail(self):
        context = self.get_context_for_emails()
        rendered_templates = self.generate_invite_mail()
        print(":::::::::::::::::::::::::::::::::::::::::::")
        send_mail(
            f"Welcome to { context['site'].name }",
            rendered_templates["text"],
            context.get("support_email_address"),
            [self.user.email],
            html_message=rendered_templates["html"],
        )
        

    def generate_invite_mail(self):
        from django.template import Template, Context

        context = self.get_context_for_emails()
        
        # Fetch the email confirmation template content (assuming you have it stored in the context)
        email_confirmation = context.get("email_confirmation")

        if email_confirmation:
            # Create a Django Template object from the email content
            email_content_template = Template(email_confirmation.email_content)

            # Render the template with the current context
            rendered_email_content = email_content_template.render(Context(context))

            # Update the context with the rendered email content
            context["email_confirmation_content"] = rendered_email_content
        else:
            # If no custom email template is found, use a default message with templating
            default_message_template = Template(
                "<p>Dear {{ profile.name }} </p>"
                "<p>Welcome to {{ constellation }}.</p>"
                "<p><em>(Copy goes here to mention terms of service and community guidelines)</em></p>"
                "<p>If you have any problems logging in, or you have not attempted to log in, please <a href='mailto:{{ support_email_address }}'>contact support.</a></p>"
            )
            
            context["email_confirmation_content"] = default_message_template.render(Context(context))


        # Now render the invite email as plain text and MJML
        rendered_invite_txt = render_to_string(
            "invite_new_profile.txt",
            context,
        )
        rendered_invite_html = render_to_string(
            "invite_new_profile.mjml.html",
            context,
        )

        # Optionally, view the rendered HTML in the browser for testing/debugging
        from cl8.utils.templating import view_rendered_html_in_browser
        view_rendered_html_in_browser(rendered_invite_html)

        return {"text": rendered_invite_txt, "html": rendered_invite_html}

class Constellation(models.Model):
    """
    A Constellation is a name we give to a specific 'container' for the members
    using constellate. Constellations might have a description, some specific welcome text, and logo to members recognise it.
    """

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profiles",
        verbose_name="site",
    )

    logo = models.ImageField(
        _("logo"),
        blank=True,
        null=True,
        max_length=200,
        upload_to="logos",
    )
    background_color = models.CharField(
        blank=True,
        max_length=256,
        help_text="A hex code colour to use for the header background colour",
    )
    text_color = models.CharField(
        blank=True,
        max_length=256,
        help_text="A hex code colour to use for the header text colour",
    )
    favicon = models.ImageField(
        _("favicon"),
        blank=True,
        null=True,
        max_length=200,
        upload_to="favicons",
    )
    welcome_message = models.TextField(null=True, blank=True)
    welcome_heading = models.TextField(null=True, blank=True)
    button = models.TextField(null=True, blank=True)


    signin_via_slack = models.BooleanField(default=False)
    signin_via_email = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.site.name}"


class CATJoinRequest(models.Model):
    joined_at = models.DateTimeField()
    email = models.EmailField(unique=False)
    city_country = models.CharField(blank=True, max_length=256)
    # Why are you interested in joining?
    why_join = models.TextField(blank=True)
    # What's the main thing you'd like to offer as a part of the community?
    main_offer = models.TextField(blank=True)

    def __str__(self):
        return f"{self.joined_at.strftime('%Y-%m-%d')} - {self.email}"

    def bio_text_from_join_request(self):
        """
        Return a markdown version of the responses given when joining. Used to fill
        out a member's profile.
        """
        return f"""
### Why are you interested in joining?

{self.why_join}


### What's the main thing you'd like to offer as a part of the community?
{self.main_offer}
"""

    class Meta:
        indexes = [models.Index(fields=["email", "joined_at"])]


class SendInviteEmailContent(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="email_confirm_template",
    )

    email_title = models.TextField(
        blank=True,
        null=True,
        help_text="Enter the subject of the email. For the site name, use `{{ constellation.site.name }}`.",
        default="Welcome to {{ constellation.site.name }}"
    )
    email_content = models.TextField(
        blank=True,
        help_text=(
            "Enter the body of the email. "
            "Use `{{ profile.name }}` for the user's name , `{{ constellation }}` for the site name and {{ support_email_address }} for the support email adrdress."
        ),
        default=(
            "<p>Dear {{ profile.name }} </p>"
            "<p>Welcome to {{ constellation }}.</p>"
            "<p><em>(Copy goes here to mention terms of service and community guidelines)</em></p>"
            "<p>If you have any problems logging in, or you have not attempted to log in, please <a href='mailto:{{ support_email_address }}'>contact support.</a></p>"
        )
    )

    def __str__(self):
        return f"{self.site.name}"

class SendInviteEmailContent(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="email_confirm_template",
    )

    email_title = models.TextField(
        blank=True,
        null=True,
        help_text="Enter the subject of the email. For the site name, use `{{ constellation }}`.",
        default="Welcome to {{ constellation }}"
    )
    email_content = models.TextField(
        blank=True,
        help_text=(
            "Enter the body of the email. "
            "Use `{{ profile.name }}` for the user's name , `{{ constellation }}` for the site name and {{ support_email_address }} for the support email adrdress."
        ),
        default=(
            "<p>Dear {{ profile.name }} </p>"
            "<p>Welcome to {{ constellation }}.</p>"
            "<p><em>(Copy goes here to mention terms of service and community guidelines)</em></p>"
            "<p>If you have any problems logging in, or you have not attempted to log in, please <a href='mailto:{{ support_email_address }}'>contact support.</a></p>"
        )
    )

    def __str__(self):
        return f"{self.site.name}"
    
    
class PasswordResetEmailContent(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="password_reset_template",
    )

    email_title = models.TextField(
        blank=True,
        null=True,
        help_text="Enter the subject of the email. For the site name, use `{{ constellation }}`.",
        default="Password Reset Request for {{ constellation }}"
    )
    email_content = models.TextField(
        blank=True,
        help_text=(
            "Enter the body of the email. "
            "Use `{{ profile.name }}` for the user's username, `{{ reset_link }}` for the password reset link, and `{{ constellation }}` for the site name."
        ),
        default=(
            "<p>Hello {{ profile.name }},</p>"
            "<p>You requested a password reset for your account on {{ constellation }}.</p>"
            "<p>Click the link below to reset your password:</p>"
            "<p><a href='{{ reset_link }}'>Reset Password</a></p>"
            "<p>If you did not request this email, please ignore it.</p>"
            "<p>Thank you!</p>"
        )
    )

    def __str__(self):
        return f"Password Reset Template for {self.site.name}"