import pytest
from backend.users.models import User, Profile
from pathlib import Path

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.username}/"


class TestProfile:
    def test_user_profile(self, profile: Profile):
        assert profile.email == profile.user.email

    def test_check_for_admin_status(self, profile: Profile):

        profile.user.is_staff = True
        profile.save()

        assert profile.admin is True

    def test_profile_photo_thumbs(self, fake_photo_profile: Profile):

        pic = fake_photo_profile.thumbnail_photo
        pa = Path()
        pic_path = pa.joinpath(pic.storage.base_location, pic.name)

        assert Path.exists(pic_path)


