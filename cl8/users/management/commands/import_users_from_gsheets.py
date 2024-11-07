import logging

from django.core.management import BaseCommand

from cl8.users.importers import (
    EmptyJoinRequestCAT,
    create_join_request_from_row,
    create_user_from_join_request,
    fetch_full_data_from_gsheet,
)

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    help = "Import user profiles into this constellation "

    def handle(self, *args, **kwargs):
        imported_users = []
        join_requests = fetch_full_data_from_gsheet()

        for req in join_requests[1:]:
            try:
                from ... import models

                join_email = req[1]
                sign_up_at = req[0]
                join_req_exists = models.CATJoinRequest.objects.filter(email=join_email)
                if not join_req_exists:
                    join_request = create_join_request_from_row(req)
                    created_user = create_user_from_join_request(join_request)
                    imported_users.append(created_user)
                    logger.info(
                        f"created user:{created_user} and profile {created_user.profile}"
                    )

                logger.info(
                    f"Skipping import of submission by {join_email} at {sign_up_at}"
                )
            except EmptyJoinRequestCAT:
                pass
