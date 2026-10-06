from django.core.management.base import BaseCommand

from contacts.models import Contact

SAMPLE = [
    ("Ada Okafor", "ada@brightwater.example", "Brightwater Labs"),
    ("Tomas Lindqvist", "tomas@northfield.example", "Northfield Logistics"),
    ("Priya Raman", "priya@sundial.example", "Sundial Analytics"),
    ("Marcus Bell", "marcus@hollowayprint.example", "Holloway Print"),
    ("Yuki Tanaka", "yuki@fernhill.example", "Fernhill Studio"),
]


class Command(BaseCommand):
    help = "Insert a handful of sample contacts; emails that already exist are left alone"

    def handle(self, *args, **options):
        created = 0
        for name, email, company in SAMPLE:
            _, was_created = Contact.objects.get_or_create(email=email, defaults={"name": name, "company": company})
            created += was_created
        self.stdout.write(f"seeded {created} contact(s)")
