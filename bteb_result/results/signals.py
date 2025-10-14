from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ResultPDF
from .utils import process_pdf  # process_pdf function আলাদা utils.py তে রাখতে পারো

@receiver(post_save, sender=ResultPDF)
def auto_process_pdf(sender, instance, created, **kwargs):
    if created:
        process_pdf(instance)
