from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .models import Contact

log = get_task_logger(__name__)


@shared_task
def nightly_digest() -> int:
    since = timezone.now() - timedelta(days=1)
    count = Contact.objects.filter(created_at__gte=since).count()
    log.info("nightly digest: %d contact(s) created since %s", count, since.isoformat(timespec="seconds"))
    return count
