from django.core.management.base import BaseCommand

import logging
import datetime

from talentmap_api.feedback.models import FrontendSecrets
import hashlib


class Command(BaseCommand):
    help = 'Creates front-end secret pair for reporting'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        public_secret = hashlib.sha256(f"{datetime.datetime.now().timestamp()}".encode('utf-8')).hexdigest()[:10]

        while FrontendSecrets.objects.filter(public_secret=public_secret).count() > 0:
            public_secret = hashlib.sha256(public_secret).hexdigest()

        private_secret = hashlib.sha256(f"{public_secret}{datetime.datetime.now().timestamp()}".encode('utf-8')).hexdigest()[:10]

        FrontendSecrets.objects.create(public_secret=public_secret, private_secret=private_secret)

        print("Frontend secret pair created")
        print(f"Public Secret: {public_secret}")
        print(f"Private Secret: {private_secret}")
