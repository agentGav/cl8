import pytest
from backend.users.models import User, Profile
from pathlib import Path
import webbrowser

pytestmark = pytest.mark.django_db


def view_rendered_html_in_browser(string_template):
    """
    Accepts a string, containing generated HTML template
    then opens it in the default browser on a computer
    """

    # show the rendered html
    with open("email_test.html", "w+") as f:
        f.write(string_template)

    webbrowser.open("email_test.html")


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

        assert profile.admin == True

    def test_send_invite_for_profile(self, profile: Profile, mailoutbox):
        profile.send_invite_mail()
        assert len(mailoutbox) == 1

    def test_generate_invite_for_profile(self, profile: Profile, mailoutbox):

        rendered_templates = profile.generate_invite_mail()

        # uncomment this to view the rendered mjml/html template
        # view_rendered_html_in_browser(rendered_templates['html'])

        # uncomment this to view the rendered text template
        # view_rendered_html_in_browser(rendered_templates['text'])

        assert "html" in rendered_templates
        assert "text" in rendered_templates

    @pytest.mark.only
    def test_clusters_as_tags(self, profile: Profile):
        """
        We represent clusters as tags,
        """

        profile.clusters.add("Open Energy")
        profile.save()

        assert "Open Energy" in [tag_name for tag_name in profile.clusters.names()]
