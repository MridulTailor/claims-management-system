import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from claims.models import Claim, ClaimDetail

class Command(BaseCommand):
    help = 'Load CSV claim data into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            help='Overwrite existing data',
        )
        parser.add_argument(
            '--claims-file',
            type=str,
            default='data/claim_list_data.csv',
            help='Path to claims CSV file'
        )
        parser.add_argument(
            '--details-file',
            type=str,
            default='data/claim_detail_data.csv',
            help='Path to claim details CSV file'
        )

    def handle(self, *args, **options):
        claims_file = options['claims_file']
        details_file = options['details_file']
        overwrite = options['overwrite']

        self.stdout.write(
            self.style.SUCCESS('Starting CSV data import...')
        )

        # Check if files exist
        if not os.path.exists(claims_file):
            self.stdout.write(
                self.style.ERROR(f'Claims file not found: {claims_file}')
            )
            return

        if not os.path.exists(details_file):
            self.stdout.write(
                self.style.ERROR(f'Details file not found: {details_file}')
            )
            return

        # Clear existing data if overwrite flag is set
        if overwrite:
            self.stdout.write('Clearing existing data...')
            ClaimDetail.objects.all().delete()
            Claim.objects.all().delete()

        # Load claims data
        claims_loaded = 0
        with open(claims_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                try:
                    claim, created = Claim.objects.get_or_create(
                        id=int(row['id']),
                        defaults={
                            'patient_name': row['patient_name'],
                            'billed_amount': float(row['billed_amount']),
                            'paid_amount': float(row['paid_amount']),
                            'status': row['status'],
                            'insurer_name': row['insurer_name'],
                            'discharge_date': datetime.strptime(row['discharge_date'], '%Y-%m-%d').date()
                        }
                    )
                    if created:
                        claims_loaded += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error loading claim {row.get("id", "unknown")}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Loaded {claims_loaded} claims')
        )

        # Load claim details
        details_loaded = 0
        with open(details_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                try:
                    claim_id = int(row['claim_id'])
                    if Claim.objects.filter(id=claim_id).exists():
                        detail, created = ClaimDetail.objects.get_or_create(
                            claim_id=claim_id,
                            defaults={
                                'denial_reason': row['denial_reason'] if row['denial_reason'] != 'N/A' else None,
                                'cpt_codes': row['cpt_codes']
                            }
                        )
                        if created:
                            details_loaded += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping detail for non-existent claim: {claim_id}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error loading detail for claim {row.get("claim_id", "unknown")}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Loaded {details_loaded} claim details')
        )

        # Summary statistics
        total_claims = Claim.objects.count()
        total_details = ClaimDetail.objects.count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Data import complete - Summary:')
        self.stdout.write(f'  Total Claims in Database: {total_claims}')
        self.stdout.write(f'  Total Details in Database: {total_details}')
        self.stdout.write(f'  Claims by Status:')
        
        for status_data in Claim.objects.values('status').distinct():
            count = Claim.objects.filter(status=status_data['status']).count()
            self.stdout.write(f'    {status_data["status"]}: {count}')
        
        self.stdout.write('='*50)
        self.stdout.write(
            self.style.SUCCESS('CSV data import completed successfully!')
        )
