import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.conf import settings

from .provider import SlackProvider


class SlackOpenIdCcnnectAdapter(OAuth2Adapter):
    """
    An updated slack adapter designed to use the updated openid connect
    flow as opposed to the deprecated auth2, identity-based flow.
    """

    provider_id = SlackProvider.id

    access_token_url = "https://slack.com/api/openid.connect.token"
    identity_url = "https://slack.com/api/openid.connect.userInfo"

    @property
    def authorize_url(self):
        """
        Return the authorise url, allowing for a custom
        authorise url to be explicit about the slack
        workspace to auth to.
        """
        if settings.SLACK_SIGNIN_AUTHORIZE_URL:
            return settings.SLACK_SIGNIN_AUTHORIZE_URL

        # otherwise return our default url
        return "https://slack.com/openid/connect/authorize"

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_data(self, token):
        hed = {"Authorization": "Bearer " + token}
        resp = requests.get(self.identity_url, headers=hed)
        resp = resp.json()

        if not resp.get("ok"):
            raise OAuth2Error()
        return resp


oauth2_login = OAuth2LoginView.adapter_view(SlackOpenIdCcnnectAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SlackOpenIdCcnnectAdapter)
