import shutil
from pathlib import Path

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.files.images import ImageFile
from django.test import RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, RequestsClient

from cl8.users.api.serializers import ProfileSerializer
from cl8.users.api.views import ProfilePhotoUploadView, ProfileViewSet
from cl8.users.models import Profile, User
from cl8.users.tests.factories import ProfileFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestProfileViewSet:
    @pytest.mark.parametrize(
        "visible,profile_count",
        [
            (True, 1),
            (False, 0),
        ],
    )
    def test_get_queryset(
        self, profile: Profile, rf: RequestFactory, visible, profile_count
    ):
        profile.visible = visible
        profile.save()
        view = ProfileViewSet()
        request = rf.get("/fake-url/")
        request.user = profile.user
        view.request = request

        assert len(view.get_queryset()) is profile_count

    def test_me(self, profile_with_tags: Profile, rf: RequestFactory):
        view = ProfileViewSet()
        request = rf.get("/fake-url/")
        request.user = profile_with_tags.user

        view.request = request
        response = view.me(request)

        for prop in [
            "name",
            "email",
            "website",
            "social_1",
            "social_2",
            "social_3",
            "visible",
        ]:
            assert response.data[prop] == getattr(profile_with_tags, prop)

        # we need to check separately for tags, as they use
        # their own manager
        response.data["tags"] = [tag for tag in profile_with_tags.tags.all()]

    def test_tag_serialised_data_structure(self, profile: Profile, rf: RequestFactory):
        view = ProfileViewSet()
        request = rf.get("/fake-url/")
        request.user = profile.user

        # set our tags
        profile.tags.add("first tag", "second tag", "third tag")
        profile.save()

        view.request = request
        response = view.me(request)
        tags = response.data["tags"]

        # are they following the structure we expect?
        for tag in tags:
            for k in ["id", "name", "slug"]:
                assert k in tag.keys()

    def test_create_profile(self, profile: Profile, rf: RequestFactory, mailoutbox):
        """
        Given: a post with correct payload
        Then: create a profile in the database, but do not send notification email

        """
        view = ProfileViewSet()
        request = rf.get("/fake-url/")

        # we assume we have a workng user
        request.user = profile.user

        # profile_data = ProfileFactory()
        profile_dict = {
            "phone": "9329275526",
            "website": "http://livingston.biz",
            "social_1": "paul58",
            "social_2": "fday",
            "social_3": "wpalmer",
            "name": "Long Name with lots of letters",
            "email": "email@somesite.com",
            "tags": ["tech, 'something else'', "],
            "bio": "Themselves TV western under. Tv can beautiful we throughout politics treat both. Fear speech left get answer over century.",
            "visible": False,
        }

        request.data = profile_dict
        # request.data = profile_data

        response = view.create(request)
        assert response.status_code == 201
        assert len(mailoutbox) == 0

    def test_create_staff_profile(
        self, profile: Profile, moderator_group: Group, rf: RequestFactory
    ):
        view = ProfileViewSet()
        request = rf.get("/fake-url/")
        request.user = profile.user

        profile_data = ProfileFactory()
        profile_dict = {
            "phone": "9329275526",
            "website": "http://livingston.biz",
            "social_1": "paul58",
            "social_2": "fday",
            "social_3": "wpalmer",
            "name": "Long Name with lots of letters",
            "email": "email@somesite.com",
            "tags": ["tech, 'something else'', "],
            "bio": "Themselves TV western under. Tv can beautiful we throughout politics treat both. Fear speech left get answer over century.",
            "visible": False,
            "admin": True,
        }

        request.data = profile_dict

        response = view.create(request)
        new_profile = Profile.objects.get(pk=response.data["id"])

        # add the user log into the backend?
        assert new_profile.user.is_staff
        # are they in the required group to administer users?
        assert moderator_group in new_profile.user.groups.all()

        assert response.status_code == 201

    def test_create_profile_and_notify(
        self, profile: Profile, rf: RequestFactory, mailoutbox, test_constellation
    ):
        view = ProfileViewSet()
        request = rf.get("/fake-url/")
        request.user = profile.user

        profile_data = ProfileFactory()
        profile_dict = {
            "phone": "9329275526",
            "website": "http://livingston.biz",
            "social_1": "paul58",
            "social_2": "fday",
            "social_3": "wpalmer",
            "name": "Long Name with lots of letters",
            "email": "email@somesite.com",
            "tags": ["tech, 'something else'', "],
            "bio": "Themselves TV western under. Tv can beautiful we throughout politics treat both. Fear speech left get answer over century.",
            "visible": False,
            "sendInvite": True,
        }

        request.data = profile_dict
        response = view.create(request)

        assert response.status_code == 201
        assert len(mailoutbox) == 1

    def test_update_profile(self, profile: Profile, rf: RequestFactory):
        view = ProfileViewSet()
        request = rf.get(f"/api/profiles/{profile.id}/")
        request.user = profile.user

        profile_data = ProfileFactory()
        profile_dict = {
            "phone": "9329275526",
            "website": "http://livingston.biz",
            "social_1": "paul58",
            "social_2": "fday",
            "social_3": "wpalmer",
            "name": "Long Name with lots of letters",
            "email": "email@somesite.com",
            "tags": ["tech"],
            "bio": "Themselves TV western under. Tv can beautiful we throughout politics treat both. Fear speech left get answer over century.",
            "visible": False,
        }

        request.data = profile_dict

        response = view.update(request, profile)
        assert response.status_code == 200

    def test_resend_invite_sends_an_email(
        self, profile: Profile, rf: RequestFactory, mailoutbox, test_constellation
    ):
        view = ProfileViewSet()
        request = rf.post(f"/profiles/{profile.id}/resend_invite/")
        request.user = profile.user
        response = view.resend_invite(request, id=profile.id)

        assert response.status_code == 200
        assert "invite has been re-sent" in response.data["message"]
        assert profile.email in response.data["message"]
        assert len(mailoutbox) == 1


class TestProfileUploadView:
    def test_file_upload_for_profile(self, profile, rf, tmp_path, tmp_pic_path):
        view = ProfilePhotoUploadView()
        request = rf.get("/upload/")
        request.user = profile.user
        view.request = request

        assert not profile.photo

        test_pic = open(tmp_pic_path, "rb")
        upload_file = ImageFile(test_pic, name="upload_pic.png")

        request.data = {
            "photo": upload_file,
            "id": profile.id,
        }

        response = view.put(request, profile.id)
        updated_profile = Profile.objects.get(pk=profile.id)

        assert response.status_code == 200
        assert updated_profile.photo
