import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import SlackProvider


class SlackOpenIdCcnnectAdapter(OAuth2Adapter):
    provider_id = SlackProvider.id

    # access_token_url = "https://slack.com/api/oauth.access"
    access_token_url = "https://slack.com/api/openid.connect.token"
    # authorize_url = "https://slack.com/oauth/authorize"
    # authorize_url = "https://slack.com/openid/connect/authorize"
    authorize_url = "https://climate-tech.slack.com/openid/connect/authorize"

    # identity_url = "https://slack.com/api/users.identity"
    identity_url = "https://slack.com/api/openid.connect.userInfo"

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
