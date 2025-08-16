from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date
from claims.models import Claim, ClaimDetail, ClaimFlag, ClaimNote

class ClaimTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test claim
        self.claim = Claim.objects.create(
            id=99999,
            patient_name='Test Patient',
            billed_amount=Decimal('1000.00'),
            paid_amount=Decimal('500.00'),
            status='Under Review',
            insurer_name='Test Insurance',
            discharge_date=date.today()
        )
        
        # Create claim detail
        self.detail = ClaimDetail.objects.create(
            claim=self.claim,
            denial_reason='Test denial reason',
            cpt_codes='99201,99202,99203'
        )

    def test_claims_list_view(self):
        """Test main claims list view"""
        response = self.client.get(reverse('claims_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')
        self.assertContains(response, 'Claims Management System')

    def test_claim_detail_view(self):
        """Test claim detail view"""
        response = self.client.get(reverse('claim_detail', args=[self.claim.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')
        self.assertContains(response, '99201,99202,99203')

    def test_search_functionality(self):
        """Test search functionality"""
        response = self.client.get(reverse('claims_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')

    def test_status_filter(self):
        """Test status filtering"""
        response = self.client.get(reverse('claims_list'), {'status': 'Under Review'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')

    def test_insurer_filter(self):
        """Test insurer filtering"""
        response = self.client.get(reverse('claims_list'), {'insurer': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Patient')

    def test_flag_claim_authenticated(self):
        """Test claim flagging with authentication"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('flag_claim', args=[self.claim.id]), {
            'reason': 'Test flag reason'
        })
        self.assertEqual(response.status_code, 302)
        
        # Check flag was created
        flag = ClaimFlag.objects.get(claim=self.claim, user=self.user)
        self.assertEqual(flag.reason, 'Test flag reason')

    def test_flag_claim_unauthenticated(self):
        """Test flag protection without authentication"""
        response = self.client.post(reverse('flag_claim', args=[self.claim.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_add_note_authenticated(self):
        """Test note addition with authentication"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_note', args=[self.claim.id]), {
            'content': 'Test note content',
            'note_type': 'User Note'
        })
        self.assertEqual(response.status_code, 302)
        
        # Check note was created
        note = ClaimNote.objects.get(claim=self.claim, user=self.user)
        self.assertEqual(note.content, 'Test note content')

    def test_admin_dashboard(self):
        """Test admin dashboard"""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Analytics Dashboard')

    def test_htmx_detail_view(self):
        """Test HTMX detail view"""
        response = self.client.get(
            reverse('claim_detail', args=[self.claim.id]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'HTMX-powered detail view')

    def test_model_underpayment_calculation(self):
        """Test underpayment calculation"""
        expected_underpayment = self.claim.billed_amount - self.claim.paid_amount
        self.assertEqual(self.claim.underpayment_amount, expected_underpayment)

    def test_model_is_flagged_property(self):
        """Test flagged property"""
        self.assertFalse(self.claim.is_flagged)
        
        # Add flag
        ClaimFlag.objects.create(
            claim=self.claim,
            user=self.user,
            reason='Test flag'
        )
        
        # Refresh from database
        self.claim.refresh_from_db()
        self.assertTrue(self.claim.is_flagged)

    def test_cpt_codes_list_property(self):
        """Test CPT codes parsing"""
        expected_codes = ['99201', '99202', '99203']
        self.assertEqual(self.detail.cpt_codes_list, expected_codes)

    def test_invalid_claim_404(self):
        """Test with invalid claim IDs"""
        response = self.client.get(reverse('claim_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)
