from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Claim(models.Model):
    """Main claim model"""
    STATUS_CHOICES = [
        ('Denied', 'Denied'),
        ('Paid', 'Paid'),
        ('Under Review', 'Under Review'),
    ]
    
    id = models.IntegerField(primary_key=True)
    patient_name = models.CharField(max_length=200)
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    insurer_name = models.CharField(max_length=200)
    discharge_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['insurer_name']),
            models.Index(fields=['discharge_date']),
            models.Index(fields=['patient_name']),
            models.Index(fields=['billed_amount']),
        ]
        
    def __str__(self):
        return f"Claim {self.id} - {self.patient_name}"
    
    @property
    def underpayment_amount(self):
        """Calculate underpayment amount"""
        return self.billed_amount - self.paid_amount
    
    @property 
    def patient_id(self):
        """Generate patient ID from claim ID for display"""
        return f"P{self.id:06d}"
    
    @property
    def is_flagged(self):
        return self.claim_flags.exists()

class ClaimDetail(models.Model):
    """Detailed claim information"""
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='details')
    denial_reason = models.TextField(blank=True, null=True)
    cpt_codes = models.TextField()
    
    def __str__(self):
        return f"Details for Claim {self.claim.id}"
    
    @property
    def cpt_codes_list(self):
        """Split CPT codes into a list"""
        return [code.strip() for code in self.cpt_codes.split(',') if code.strip()]

class ClaimFlag(models.Model):
    """Flag system for claim review"""
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='claim_flags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=500, default='Flagged for review')
    flagged_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['claim', 'user']
        ordering = ['-flagged_at']
    
    def __str__(self):
        return f"Flag on Claim {self.claim.id} by {self.user.username}"

class ClaimNote(models.Model):
    """Annotation system for claims"""
    NOTE_TYPES = [
        ('User Note', 'User Note'),
        ('Admin Note', 'Admin Note'),
        ('System Flag', 'System Flag'),
    ]
    
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='claim_notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='User Note')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.note_type} on Claim {self.claim.id} by {self.user.username}"
