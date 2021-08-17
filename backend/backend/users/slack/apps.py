from django.apps import AppConfig


class SlackOpenIDConnectConfig(AppConfig):
    """
    An application to hold the config necessary for
    using allauthn with the newer openid connect sign in methods.
    """

    name = "backend.users.slack"
    label = name  # added to avoid clashing with allauth slack label
    verbose_name = "Slack OpenID Connect"
