import csv

# once we have that we iterate through each row, and create a user and the
# necessary tags
import logging
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.text import slugify
import slack

from backend.users.models import Profile, User

# How it works

# We instantiate the CSV import, and either load the path to the file,
# or load the file directly.


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class NoEmailFound(Exception):
    pass


class ProfileImporter:

    rows = []

    def load_csv_from_path(self, import_path: Path = None):
        with open(import_path) as csvfile:
            self.load_csv(csvfile)

    def load_csv(self, csvfile=None):
        # Loads the rows contents of a CSV, returning an datastructure
        self.rows = []

        reader = csv.DictReader(csvfile)

        for row in reader:
            self.rows.append(row)

    def create_users(self, rows=None):
        if not rows:
            rows = self.rows

        created_users = []
        skipped_users = []

        for count, row in enumerate(rows):

            logger.debug(f"{count}, {row['name']}, rows to run through: {len(rows)}")
            try:
                new_user = self.create_user(row)
                created_users.append(new_user)
            except NoEmailFound:
                skipped_users.append(row)

        logger.debug(f"Added {len(created_users)}")
        logger.debug(f"Skipped {len(created_users)}")

        return created_users

    def add_tags_to_profile(
        self, profile: Profile, row: OrderedDict, columns: List = None
    ):
        """
        Take a profile object, and add all the relevant tags,
        in the properties from the CSV listed `columns`.
        """
        if not columns:
            columns = ["tags"]

        for colname in columns:
            tags = row.get(colname)
            # exit early
            if not tags:
                continue

            for tag in tags.split(","):
                profile.tags.add(tag.strip())

        return profile

    def create_user(self, row):
        """
        Accepts a row, and returns the corresponding user generated based
        on the info passed in
        """
        if not row["email"]:
            raise (NoEmailFound)
            return None

        # create django user
        safer_int = str(datetime.now().microsecond)[:4]
        safer_name = f"{slugify(row['name'])}-{safer_int}"

        user, created = User.objects.get_or_create(
            name=row["name"], email=row["email"], username=safer_name
        )

        logger.debug(user)
        user.save()
        logger.debug(user.id)

        visible = True

        profile, created = Profile.objects.get_or_create(
            user=user,
            phone=row.get("phone"),
            website=row.get("website"),
            twitter=row.get("twitter"),
            facebook=row.get("facebook"),
            linkedin=row.get("linkedin"),
            bio=row.get("bio"),
            visible=visible,
            photo=self.fetch_user_pic(row.get("photo")),
        )

        logger.debug(f"profile: {profile}")
        logger.debug(f"user: {user}")
        logger.debug(profile.user.id)

        return user

    def fetch_user_pic(self, url: str = None):
        """
        """
        if not url:
            return None

        res = requests.get(url)

        if res.content:
            return ImageFile(res.content)


class SlackImporter:
    """
    An importer for fetching a list of users from a given channel in
    a slack workspace, then adding each user to a given constellation.
    """

    def _fetch_user_ids(self):
        """Fetch a list of usrs from slack"""

        client = slack.WebClient(token=settings.SLACK_TOKEN)
        channel_id = self._id_for_channel_name(settings.SLACK_CHANNEL_NAME)

        client.conversations_members(channel=channel_id).data
        pass

    def _id_for_channel_name(self, channel_name):
        """
        Accept a channel name, and return the channel id for further use
        with slack API
        """

        pass

    def list_new_usrs(self):
        """
        Return a list of user ids for users that
        do not already exist in the constellation
        """

        # TODO: figure out if we use email, or store the slack ID?
        pass

    def import_slack_user(self, user_id):
        """
        Accept a user id, fetch the matching user
        from slack, and import it into the constellation
        """

        # fetch the user object from slack
        # slack_user = client.users_info(user=user_id).data

        # add the user to constellate

        # add the matching profile to constellate for user

        # return the profile

        pass

    def import_users(self):
        """
        Fetch users from slack for a channel,
        and import all the new users.
        """

        user_ids = self._fetch_user_ids()

        new_ids = self.list_new_usrs(user_ids)

        imported_users = []
        for new_user_id in new_ids:
            imported_user = self.import_slack_user(new_user_id)
            imported_users.append(imported_user)

        return imported_users
