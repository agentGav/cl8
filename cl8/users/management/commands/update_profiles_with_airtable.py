import logging

from django.core.management import BaseCommand
from cl8.users.importers import CATAirtableImporter
from pathlib import Path

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
# console.setLevel(logging.DEBUG)
# logger.addHandler(console)
# logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    help = (
        "Import update existing profiles with corresponding "
        "info from directory airtable"
    )

    def handle(self, *args, **kwargs):
        importer = CATAirtableImporter()
        rows = importer.fetch_data_from_airtable()

        users = importer.update_profiles_from_rows(rows)
        logger.debug(f"imported: {users}")
