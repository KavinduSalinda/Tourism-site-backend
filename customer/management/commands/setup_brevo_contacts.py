from django.core.management.base import BaseCommand
from django.conf import settings
from customer.models import Newsletter
from utils.brevo_contacts import get_brevo_contact_lists, add_contact_to_brevo


class Command(BaseCommand):
    help = 'Setup Brevo contact lists and sync existing newsletter subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list-contacts',
            action='store_true',
            help='List all available contact lists in Brevo',
        )
        parser.add_argument(
            '--sync-subscribers',
            action='store_true',
            help='Sync verified newsletter subscribers to Brevo',
        )

    def handle(self, *args, **options):
        if not settings.SENDINBLUE_API_KEY:
            self.stdout.write(
                self.style.ERROR('SENDINBLUE_API_KEY not configured in settings')
            )
            return

        if options['list_contacts']:
            self.list_contact_lists()
        elif options['sync_subscribers']:
            self.sync_subscribers()
        else:
            self.stdout.write(
                self.style.WARNING('Please specify --list-contacts or --sync-subscribers')
            )

    def list_contact_lists(self):
        """List all available contact lists in Brevo"""
        self.stdout.write('Fetching Brevo contact lists...')
        
        try:
            lists = get_brevo_contact_lists()
            if lists:
                self.stdout.write(self.style.SUCCESS(f'Found {len(lists)} contact lists:'))
                for contact_list in lists:
                    self.stdout.write(f'  - ID: {contact_list.id}, Name: {contact_list.name}')
            else:
                self.stdout.write(self.style.WARNING('No contact lists found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching contact lists: {e}'))

    def sync_subscribers(self):
        """Sync verified newsletter subscribers to Brevo"""
        self.stdout.write('Syncing verified newsletter subscribers to Brevo...')
        
        verified_subscribers = Newsletter.objects.filter(is_verified=True)
        count = 0
        
        for subscriber in verified_subscribers:
            try:
                attributes = {
                    "SUBSCRIPTION_DATE": subscriber.created_at.strftime("%Y-%m-%d"),
                    "VERIFICATION_DATE": subscriber.verified_at.strftime("%Y-%m-%d") if subscriber.verified_at else "",
                    "SOURCE": "Website Newsletter"
                }
                
                if add_contact_to_brevo(subscriber.email, attributes):
                    count += 1
                    self.stdout.write(f'  ✓ Added {subscriber.email}')
                else:
                    self.stdout.write(f'  ✗ Failed to add {subscriber.email}')
                    
            except Exception as e:
                self.stdout.write(f'  ✗ Error adding {subscriber.email}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully synced {count} out of {verified_subscribers.count()} subscribers')
        ) 