from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class ClaimsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'claims'

    def ready(self):
        post_migrate.connect(load_initial_data, sender=self)


@receiver(post_migrate)
def load_initial_data(sender, **kwargs):
    """Auto-load CSV data on first migration"""
    if sender.name == 'claims':
        from .models import Claim
        from django.core.management import call_command
        import os
        
        # Only load data if database is empty
        if Claim.objects.count() == 0:
            # Check if CSV files exist
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            claims_file = os.path.join(data_dir, 'claim_list_data.csv')
            details_file = os.path.join(data_dir, 'claim_detail_data.csv')
            
            if os.path.exists(claims_file) and os.path.exists(details_file):
                print("🔄 Auto-loading CSV data on first run...")
                try:
                    call_command('load_claims_data')
                    print("✅ CSV data loaded successfully!")
                except Exception as e:
                    print(f"❌ Error loading CSV data: {e}")
            else:
                print("⚠️ CSV files not found - skipping auto-load")
