import logging
from django_htmx.http import trigger_client_event
from django.template.loader import render_to_string
from dal import autocomplete
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core import paginator
from django.core.files.images import ImageFile
from django.db.models import Case, When
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import resolve, reverse
from django.utils.text import slugify
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from allauth.account.adapter import DefaultAccountAdapter
from django.template import Template, Context
from django.utils.translation import gettext as _
from allauth.account.utils import filter_users_by_email

from markdown_it import MarkdownIt
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)

from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from taggit.models import Tag

from ..filters import ProfileFilter
from ..forms import ProfileUpdateForm, ProfileCreateForm
from ..models import Cluster, Profile, Constellation, PasswordResetEmailContent
from .serializers import (
    ClusterSerializer,
    ProfilePicSerializer,
    ProfileSerializer,
    TagSerializer,
    
)

User = get_user_model()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
NO_PROFILES_PER_PAGE = 100


def fetch_profile_list(request: HttpRequest, ctx: dict):
    """
    Fetch the list of profiles for the given set of params, and
    populate the provided context dictionary
    """
    filtered_profiles = ProfileFilter(
        request.GET,
        queryset=Profile.objects.filter(visible=True).prefetch_related("tags", "user"),
    )

    ctx["profile_filter"] = filtered_profiles

    # because we're using full text search with postgres, we need to de-dupe the results
    # while preserving their order. We'd normally do this using a distinct() call, but
    # because we have multiple instances of the same profile in the queryset, with different
    # 'rank' scores. The ORM with Postgres does not let us order by 'rank' if we don't include
    # it as a field we are calling distinct on, and doing that would stop us being able to dedupe
    # the results.
    # So instead we need to manually dedupe the results by id, and then order by that.
    ordered_profile_ids = []
    for prof in filtered_profiles.qs:
        if prof.id not in ordered_profile_ids:
            ordered_profile_ids.append(prof.id)
    # once we have a deduped list of ids, we need to convert it back into a queryset,
    # so code that expects a queryset can still work.
    # Querysets do not guarantee order so for Postgres we need to Case() to create a
    # SQL statement that preserves the order defined above, and then order by that.

    # This is a bit dense, but the code below creates a Case() with a list comprehension that
    # creates a list of When's that look like this:
    # ORDER BY
    # CASE
    #   WHEN id=10 THEN 0
    #   WHEN id=45 THEN 1
    #   WHEN id=60 THEN 2
    # END;
    # More below:
    # https://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order

    preserved_order = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_profile_ids)]
    )

    # Finally, we can now create a new deduped Queryset, with the correct ordering, and prefetch
    # the related tags and user objects, to avoid expensive N+1 queries later on. Phew!
    ordered_deduped_profiles = (
        Profile.objects.filter(id__in=ordered_profile_ids)
        .order_by(preserved_order)
        .prefetch_related("tags", "user")
    )

    pager = paginator.Paginator(ordered_deduped_profiles, NO_PROFILES_PER_PAGE)
    page = request.GET.get("page", 1)

    try:
        ctx["paginated_profiles"] = pager.page(page)
    except paginator.PageNotAnInteger:
        ctx["paginated_profiles"] = pager.page(1)
    except paginator.EmptyPage:
        ctx["paginated_profiles"] = pager.page(paginator.num_pages)

    active_tag_ids = request.GET.getlist("tags")

    if active_tag_ids:
        from ..models import flat_tag_list

        ctx["active_tags"] = flat_tag_list(Tag.objects.filter(id__in=active_tag_ids))

    return ctx


def has_active_search(request: HttpRequest, context: dict):
    """
    Check if the request has any active search terms
    """
    search = request.GET.get("bio", None)
    tags = request.GET.get("tags", None)
    profile = context.get("profile")

    return bool(tags or search or profile)


def hide_profile_list(request: HttpRequest, context: dict):
    """
    A helper function to determine whether to hide the profile list on mobile sites.
    TODO: this might make more sense as a template tag. We should decide whether
    to move into a template tag instead.
    """
    search = request.GET.get("bio", None)
    tags = request.GET.get("tags", None)
    active_search = bool(tags or search)
    profile = context.get("profile")

    # if we have a profile, and active search - we show the profile slot, but hide the list
    if profile:
        return True

    # otherwise if we have no profile, but an active search, we show
    # the list to click through to
    if active_search:
        return False
    # if we have no profile and no active search -- we show the profile slot,
    # hiding sidebar on mobile (our profile slot has the instructions)
    return False


@login_required
def homepage(request):
    ctx = {"is_authenticated": request.user.is_authenticated}

    ctx = fetch_profile_list(request, ctx)

    should_hide_profile_list = hide_profile_list(request, ctx)

    ctx["hide_profile_list"] = should_hide_profile_list
    logger.warn(f"should_hide_profile_list: {should_hide_profile_list}")
    if request.htmx:
        template_name = "pages/_home_partial.html"

        response = render(request, template_name, ctx)
        rendered_active_tags = render_to_string("_active_tags_list.html", ctx, request)

        # passing this triggers an update of the rendering for touch devices,
        # to switch between showing a profile or a profile list

        logger.info(f"should_hide_profile_list: {should_hide_profile_list}")
        response = trigger_client_event(
            response,
            "update-profile",
            {"hide_profile_list": should_hide_profile_list},
        )

        return trigger_client_event(
            response,
            "active-tags-changed",
            {"rendered_html": rendered_active_tags},
        )

    else:
        template_name = "pages/home.html"

    return render(request, template_name, ctx)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    A template view that exposes information about the
    user being logged in
    """

    queryset = Profile.objects.all()
    slug_field = "short_id"
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        """ """
        is_authenticated = self.request.user.is_authenticated

        ctx = {
            "is_authenticated": is_authenticated,
        }

        ctx = fetch_profile_list(self.request, ctx)

        if self.object is not None:
            print("aya aya ya")
            ctx["profile"] = self.object
            active_tag_ids = self.request.GET.getlist("tags")

            md = MarkdownIt()
            if self.object.bio:
                markdown_bio = md.render(self.object.bio)
                ctx["profile_rendered_bio"] = markdown_bio

            grouped_tags, ungrouped_tags = self.object.tags_by_grouping()

            ctx["grouped_tags"] = grouped_tags
            ctx["ungrouped_tags"] = ungrouped_tags
            ctx["active_tag_ids"] = [int(tag_id) for tag_id in active_tag_ids]

        if (
            self.object.user == self.request.user
            or self.request.user.is_superuser
            or self.request.user.is_staff
        ):
            ctx["can_edit"] = True

        should_hide_profile_list = hide_profile_list(self.request, ctx)
        ctx["hide_profile_list"] = should_hide_profile_list
        
        return ctx

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if request.htmx:
            self.template_name = "_profile.html"
            response = self.render_to_response(context)

            rendered_active_tags = render_to_string(
                "_active_tags_list.html", context, request
            )
            should_hide_profile = hide_profile_list(request, context)
            response = trigger_client_event(
                response,
                "update-profile",
                {"hide_profile_list": should_hide_profile},
            )
            return trigger_client_event(
                response, "active-tags-changed", {"rendered_html": rendered_active_tags}
            )

        return self.render_to_response(context)


class ProfileEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    queryset = Profile.objects.all()
    slug_field = "short_id"
    template_name = "pages/edit_profile.html"
    form_class = ProfileUpdateForm

    def has_permission(self):
        """
        Users should only be able to edit their own profiles.
        Admins can edit any profile.
        """

        if self.request.user == self.get_object().user:
            return True

        if self.request.user.is_superuser or self.request.user.is_staff:
            return True

        return False

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()

        if "photo" in form.cleaned_data:
            form.instance.update_thumbnail_urls()
        return super().form_valid(form)

    def get_form_kwargs(self):
        """
        Return the keyword arguments for instantiating the form.
        """
        kwargs = super().get_form_kwargs()
        if hasattr(self, "object"):
            kwargs.update({"instance": self.object})
        kwargs["initial"] = {
            "name": self.object.user.name,
            "email": self.object.user.email,
        }
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Add extra context to the template.
        """
        # Fetch the default context from the superclass
        context = super().get_context_data(**kwargs)

        # Fetch additional context (e.g., profile list)
        context = fetch_profile_list(self.request, context)

        return context


class ProfileCreateView(CreateView):
    template_name = "pages/create_profile.html"
    form_class = ProfileCreateForm
    model = Profile

    def has_permission(self):
        """
        Users should only be able to edit their own profiles.
        Admins can edit any profile.
        """

        if self.request.user == self.get_object().user:
            return True

        if self.request.user.is_superuser or self.request.user.is_staff:
            return True

        return False

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """
        Add extra context to the template.
        """
        # Fetch the default context from the superclass
        context = super().get_context_data(**kwargs)

        # Fetch additional context (e.g., profile list)
        context = fetch_profile_list(self.request, context)

        return context


class ProfileViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    serializer_class = ProfileSerializer
    queryset = (
        Profile.objects.filter(visible=True)
        .prefetch_related("tags")
        .prefetch_related("clusters")
        .select_related("user")
    )
    lookup_field = "id"

    @action(detail=True, methods=["POST"])
    def resend_invite(self, request, id=None):
        assert id
        profile = Profile.objects.get(pk=id)
        try:
            profile.send_invite_mail()

            return Response(
                status=status.HTTP_200_OK,
                data={
                    "message": f"An email invite has been re-sent to {profile.email}"
                },
            )
        except Exception as exc:
            logger.error(exc)
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={
                    "message": (
                        "Sorry, we had a problem re-sending the invite email. "
                        "Please try again later."
                    )
                },
            )

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serialized_profile = ProfileSerializer(request.user.profile)
        return Response(status=status.HTTP_200_OK, data=serialized_profile.data)

    def create(self, request):
        """
        Create a profile for the given user, adding them to
        the correct admin group, and sending an optional invite
        """

        send_invite = request.data.get("sendInvite")

        serialized_profile = ProfileSerializer(data=request.data)
        serialized_profile.is_valid(raise_exception=True)
        new_profile = serialized_profile.create(serialized_profile.data)

        full_serialized_profile = ProfileSerializer(new_profile)

        if new_profile.user.is_staff:
            mod_group_name = settings.MODERATOR_GROUP_NAME
            moderators = Group.objects.get(name=mod_group_name)
            new_profile.user.groups.add(moderators)
            new_profile.user.save()
            new_profile.save()
        if send_invite:
            new_profile.send_invite_mail()

        headers = self.get_success_headers(full_serialized_profile.data)
        return Response(
            full_serialized_profile.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_object(self):
        """
        Override the standard request to allow a user to see
        their own profile, even when it's hidden.
        """

        # First the boiler plate
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # now our check for when a user is hidden but also logged in
        current_user = self.request.user

        if current_user.profile.id == int(filter_kwargs.get("id")):
            if current_user.has_profile():
                return current_user.profile

        # otherwise do the usual
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        inbound_data = request.data.copy()

        profile_id = resolve(request.path).kwargs["id"]
        instance = Profile.objects.get(id=profile_id)

        serialized_profile = self.serializer_class(
            instance, data=inbound_data, partial=partial
        )
        serialized_profile.is_valid(raise_exception=True)
        serialized_profile.update(instance, serialized_profile.validated_data)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serialized_profile.data)


class ProfilePhotoUploadView(APIView):
    """ """

    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, id, format=None):
        serializer = ProfilePicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = Profile.objects.get(pk=serializer.validated_data["id"])
        profile_pic = serializer.validated_data.pop("photo", None)

        if profile_pic:
            img = ImageFile(profile_pic)
            photo_path = f"{slugify(profile.name)}.png"
            profile.photo.save(photo_path, img, save=True)
            profile.update_thumbnail_urls()

        return Response(ProfileSerializer(profile).data)


class ClusterViewSet(
    # RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    serializer_class = ClusterSerializer
    queryset = Cluster.objects.all()


class TagViewSet(
    # RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class TagAutoCompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Tag.objects.none()

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    CustomAccountAdapter class for handling email sending during account actions.
    
    This class overrides the default behavior of sending emails in Django
    allauth, allowing for custom templates and messages based on the current site.
    """
    
    def send_mail(self, template_prefix, email, context):
        users = filter_users_by_email(email)
        user = users[0] if users else None
        context['user'] = user

        # Check if the user exists
        if user:
            context['password_reset_url'] = self.get_password_reset_url(context)
            # User exists, get their profile
            context['profile'] = Profile.objects.get(user=user)
            email_content = self.get_email_content(context)

            # Send the email to the user
            send_mail(
                f"Welcome to {context['constellation']}",
                email_content,
                None,
                [email],
                html_message=email_content,
            )
        else:
            # User does not exist, send default email
            self.send_default_email(email)

    def send_default_email(self, email):
        current_site = get_current_site(self.request)
        subject = "Hello from Constellate!"
        message = f"""
        You are receiving this email because you, or someone else, tried to access an account with email {email}. 
        However, we do not have any record of such an account in our systems.
        
        This mail can be safely ignored if you did not initiate this action.
        
        If it was you, please contact us and we can add you.
        
        Thank you!
  
        """
        
        # Send the default email
        send_mail(
            subject,
            message,
            None,
            [email],
        )

    def get_email_content(self, context):
        current_site = get_current_site(self.request)

        # Try to get the custom email template from the database
        email_confirmation = PasswordResetEmailContent.objects.filter(site=current_site).first()

        if email_confirmation:
            # Create a Django Template object from the email content
            email_content_template = Template(email_confirmation.email_content)
            context["constellation"] = current_site.name  # Set site name
            context["reset_link"] = self.get_password_reset_url(context)  # Set password reset link
            
            # Render the template with the context
            context["password_reset_content"] = email_content_template.render(Context(context))
        else:
            # Default password reset message template
            default_message_template = Template(
                '''<p>Hello {{ profile.name }},</p>
                <p>You requested a password reset for your account on {{ constellation }}.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{{ reset_link|safe }}">Reset Password</a></p>
                <p>If you did not request this email, please ignore it.</p>
                <p>Thank you!</p>'''
            )

            # Set the necessary context variables for the default message
            context["constellation"] = current_site.name  # Set site name
            context["reset_link"] = self.get_password_reset_url(context)  # Set password reset link
            
            # Render the default template with the context
            context["password_reset_content"] = default_message_template.render(Context(context))

        print(context["password_reset_content"], "Rendered email content")  # Debug output
        return context["password_reset_content"]  # Return the rendered HTML safely

    def get_password_reset_url(self, context):
        return context['password_reset_url']
