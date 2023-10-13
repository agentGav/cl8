import logging

from django.core.management import BaseCommand
from ... import models
from cl8.users.importers import (
    EmptyJoinRequestCAT,
    add_bio_to_profile_from_join_request,
    create_join_request_from_row,
    fetch_full_data_from_gsheet,
)

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    help = (
        "Run through the all the bios in the gsheet "
        "and update the user profiles"
    )

    def handle(self, *args, **kwargs):
        updated_profiles = []
        join_requests = fetch_full_data_from_gsheet()

        for req in join_requests[1:]:
            join_email = req[1]
            sign_up_at = req[0]

            try:
                profile = models.Profile.objects.get(user__email=join_email)
            except models.Profile.DoesNotExist:
                logger.info(
                    f"Profile for {join_email} does not exist"
                )
                continue

            try:
                join_req_exists = models.CATJoinRequest.objects.filter(email=join_email)
                if not join_req_exists:
                    join_request = create_join_request_from_row(req)
                    updated_profile = add_bio_to_profile_from_join_request(profile, join_request)
                    updated_profiles.append(updated_profile)
                    logger.info(
                        f"Profile updated {updated_profile}"
                    )

                logger.info(
                    f"Skipping update for {join_email} at {sign_up_at}"
                )
            except EmptyJoinRequestCAT:
                pass
        
        logger.info(
            f"Updated {len(updated_profiles)} profiles"
        )
