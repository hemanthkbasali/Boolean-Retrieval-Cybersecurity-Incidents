from django.core.management.base import BaseCommand

from finder.models import Incident
from finder.search import load_documents


class Command(BaseCommand):
    help = "Load incidents.csv into the database table finder_incident"

    def handle(self, *args, **options):
        Incident.objects.all().delete()
        rows = load_documents()
        Incident.objects.bulk_create(
            Incident(id=i, title=r["title"], type=r["type"], description=r["description"])
            for i, r in rows.items()
        )
        self.stdout.write(f"Loaded {len(rows)} incidents into the database.")
