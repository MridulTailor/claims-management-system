from django.contrib import admin
from .models import Claim, ClaimDetail, ClaimFlag, ClaimNote

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'billed_amount', 'paid_amount', 'status', 'insurer_name', 'discharge_date', 'is_flagged']
    list_filter = ['status', 'insurer_name', 'discharge_date']
    search_fields = ['id', 'patient_name', 'insurer_name']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    def is_flagged(self, obj):
        return obj.is_flagged
    is_flagged.boolean = True
    is_flagged.short_description = 'Flagged for Review'

@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    list_display = ['claim', 'denial_reason', 'cpt_codes']
    search_fields = ['claim__id', 'claim__patient_name', 'cpt_codes']
    list_filter = ['denial_reason']

@admin.register(ClaimFlag)
class ClaimFlagAdmin(admin.ModelAdmin):
    list_display = ['claim', 'user', 'reason', 'flagged_at']
    list_filter = ['flagged_at', 'user']
    search_fields = ['claim__id', 'claim__patient_name', 'reason']
    readonly_fields = ['flagged_at']

@admin.register(ClaimNote)
class ClaimNoteAdmin(admin.ModelAdmin):
    list_display = ['claim', 'user', 'note_type', 'created_at', 'content_preview']
    list_filter = ['note_type', 'created_at', 'user']
    search_fields = ['claim__id', 'claim__patient_name', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
