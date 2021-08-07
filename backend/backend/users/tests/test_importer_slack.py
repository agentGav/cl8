import pytest


@pytest.fixture
def slack_dummy_user():
    return {
        "ok": True,
        "user": {
            "id": "XXXXXXXXX",
            "team_id": "XXXXXXXXX",
            "name": "chris",
            "deleted": False,
            "color": "df3dc0",
            "real_name": "Chris Adams",
            "tz": "Europe/Amsterdam",
            "tz_label": "Central European Summer Time",
            "tz_offset": 7200,
            "profile": {
                "title": "",
                "phone": "",
                "skype": "",
                "real_name": "Chris Adams",
                "real_name_normalized": "Chris Adams",
                "display_name": "mrchrisadams",
                "display_name_normalized": "mrchrisadams",
                "fields": None,
                "status_text": "some text",
                "status_emoji": ":some_emoji:",
                "status_expiration": 0,
                "avatar_hash": "20c4840e9641",
                "image_original": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_original.jpg",
                "is_custom_image": True,
                "email": "chris@productscience.co.uk",
                "first_name": "Chris",
                "last_name": "Adams",
                "image_24": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_24.jpg",
                "image_32": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_32.jpg",
                "image_48": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_48.jpg",
                "image_72": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_72.jpg",
                "image_192": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_192.jpg",
                "image_512": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_512.jpg",
                "image_1024": "https://avatars.slack-edge.com/2020-07-21/1276994577392_20c4840e96416dec0782_1024.jpg",
                "status_text_canonical": "",
                "team": "XXXXXXXXX",
            },
            "is_admin": True,
            "is_owner": True,
            "is_primary_owner": False,
            "is_restricted": False,
            "is_ultra_restricted": False,
            "is_bot": False,
            "is_app_user": False,
            "updated": 1614874162,
            "is_email_confirmed": True,
        },
    }


class TestSlackImporter:
    def test_fetch_users(self, slack_dummy_user):
        """
        Test that we can fetch the list of users, or user ids in a given public channel
        """

    def test_import_user(self, slack_dummy_user):
        """test that we can create a profile from a given slack payload"""
        pass

        # slack_id
        # display_name_normalized -
        # tz_label
        # profile
        # image_original
        # email

