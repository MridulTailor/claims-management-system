from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from .models import Claim, ClaimDetail, ClaimFlag, ClaimNote
import json
import logging

logger = logging.getLogger(__name__)

def claims_list(request):
    """Main claims list view with filtering and pagination"""
    try:
        claims = Claim.objects.select_related().prefetch_related(
            'details', 'claim_flags', 'claim_notes'
        ).order_by('-discharge_date')
        
        filters_applied = False
        
        search_query = request.GET.get('search', '').strip()
        if search_query:
            claims = claims.filter(
                Q(patient_name__icontains=search_query) |
                Q(id__icontains=search_query) |
                Q(insurer_name__icontains=search_query)
            )
            filters_applied = True
        
        status_filter = request.GET.get('status', '')
        if status_filter:
            claims = claims.filter(status=status_filter)
            filters_applied = True
        
        insurer_filter = request.GET.get('insurer', '')
        if insurer_filter:
            claims = claims.filter(insurer_name__icontains=insurer_filter)
            filters_applied = True
        
        min_amount = request.GET.get('min_amount', '')
        max_amount = request.GET.get('max_amount', '')
        if min_amount:
            try:
                min_val = float(min_amount)
                if min_val >= 0:
                    claims = claims.filter(billed_amount__gte=min_val)
                    filters_applied = True
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid minimum amount format.')
        if max_amount:
            try:
                max_val = float(max_amount)
                if max_val >= 0:
                    claims = claims.filter(billed_amount__lte=max_val)
                    filters_applied = True
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid maximum amount format.')
        
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        if date_from:
            try:
                claims = claims.filter(discharge_date__gte=date_from)
                filters_applied = True
            except ValidationError:
                messages.warning(request, 'Invalid date format.')
        if date_to:
            try:
                claims = claims.filter(discharge_date__lte=date_to)
                filters_applied = True
            except ValidationError:
                messages.warning(request, 'Invalid date format.')
        
        sort_field = request.GET.get('sort', 'discharge_date')
        sort_direction = request.GET.get('direction', 'desc')
        
        sort_mapping = {
            'id': 'id',
            'patient': 'patient_name',
            'insurer': 'insurer_name',
            'amount': 'billed_amount',
            'status': 'status',
            'date': 'discharge_date'
        }
        
        if sort_field in sort_mapping:
            order_field = sort_mapping[sort_field]
            if sort_direction == 'desc':
                order_field = f'-{order_field}'
            claims = claims.order_by(order_field)
        else:
            claims = claims.order_by('-discharge_date')
        
        items_per_page = request.GET.get('per_page', '25')
        try:
            items_per_page = min(int(items_per_page), 100)
        except (ValueError, TypeError):
            items_per_page = 25
        
        total_count = claims.count()
        if total_count == 0:
            context = {
                'claims': Claim.objects.none(),
                'statuses': Claim.objects.values_list('status', flat=True).exclude(status__isnull=True).exclude(status__exact='').distinct().order_by('status'),
                'insurers': Claim.objects.values_list('insurer_name', flat=True).exclude(insurer_name__isnull=True).exclude(insurer_name__exact='').distinct().order_by('insurer_name'),
                'search_query': search_query,
                'status_filter': status_filter,
                'insurer_filter': insurer_filter,
                'min_amount': min_amount,
                'max_amount': max_amount,
                'date_from': date_from,
                'date_to': date_to,
                'items_per_page': items_per_page,
                'page_range': [1],
                'total_claims': 0,
            }
            if request.headers.get('HX-Request'):
                return render(request, 'claims/claims_table_partial.html', context)
            return render(request, 'claims/claims_list_modern.html', context)
            
        paginator = Paginator(claims, items_per_page)
        page = request.GET.get('page', '1')
        
        try:
            claims = paginator.page(page)
        except PageNotAnInteger:
            claims = paginator.page(1)
        except EmptyPage:
            claims = paginator.page(paginator.num_pages)
        
        statuses = Claim.objects.values_list('status', flat=True).exclude(status__isnull=True).exclude(status__exact='').distinct().order_by('status')
        insurers = Claim.objects.values_list('insurer_name', flat=True).exclude(insurer_name__isnull=True).exclude(insurer_name__exact='').distinct().order_by('insurer_name')
        
        # Calculate pagination info for advanced navigation
        current_page = claims.number
        total_pages = paginator.num_pages
        has_previous = claims.has_previous()
        has_next = claims.has_next()
        
        # Generate smart page range for pagination
        page_range = []
        if total_pages <= 7:
            page_range = list(range(1, total_pages + 1))
        else:
            if current_page <= 4:
                page_range = list(range(1, 6)) + ['...', total_pages]
            elif current_page >= total_pages - 3:
                page_range = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
            else:
                page_range = [1, '...'] + list(range(current_page - 1, current_page + 2)) + ['...', total_pages]
        
        context = {
            'claims': claims,
            'statuses': statuses,
            'insurers': insurers,
            'search_query': search_query,
            'status_filter': status_filter,
            'insurer_filter': insurer_filter,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'date_from': date_from,
            'date_to': date_to,
            'items_per_page': items_per_page,
            'page_range': page_range,
            'total_claims': paginator.count,
        }
        
    except Exception as e:
        logger.error(f"Error in claims_list view: {str(e)}")
        messages.error(request, 'An error occurred while loading claims. Please try again.')
        claims = Claim.objects.none()
        context = {
            'claims': claims,
            'statuses': Claim.objects.values_list('status', flat=True).exclude(status__isnull=True).exclude(status__exact='').distinct().order_by('status'),
            'insurers': Claim.objects.values_list('insurer_name', flat=True).exclude(insurer_name__isnull=True).exclude(insurer_name__exact='').distinct().order_by('insurer_name'),
            'search_query': search_query,
            'status_filter': status_filter,
            'insurer_filter': insurer_filter,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'date_from': date_from,
            'date_to': date_to,
            'error': True,
        }
    
    if request.headers.get('HX-Request'):
        return render(request, 'claims/claims_table_partial.html', context)
    
    return render(request, 'claims/claims_list_modern.html', context)

def claim_detail(request, claim_id):
    """HTMX claim detail view"""
    claim = get_object_or_404(Claim, id=claim_id)
    
    context = {
        'claim': claim,
        'is_htmx': request.headers.get('HX-Request')
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'claims/claim_detail_modal.html', context)
    return render(request, 'claims/claim_detail_modern.html', context)

@login_required
@require_POST
def flag_claim(request, claim_id):
    """Flag claim for review"""
    claim = get_object_or_404(Claim, id=claim_id)
    reason = request.POST.get('reason', 'Flagged for review')
    
    flag, created = ClaimFlag.objects.get_or_create(
        claim=claim,
        user=request.user,
        defaults={'reason': reason}
    )
    
    if created:
        messages.success(request, f'Claim {claim_id} flagged for review!')
    else:
        messages.info(request, f'Claim {claim_id} already flagged by you.')
    
    if request.headers.get('HX-Request'):
        return render(request, 'claims/claim_flag_status.html', {'claim': claim})
    
    return redirect('claim_detail', claim_id=claim_id)

@login_required
@require_POST
def add_note(request, claim_id):
    """Add note to claim"""
    claim = get_object_or_404(Claim, id=claim_id)
    content = request.POST.get('content', '').strip()
    note_type = request.POST.get('note_type', 'User Note')
    
    if content:
        note = ClaimNote.objects.create(
            claim=claim,
            user=request.user,
            content=content,
            note_type=note_type
        )
        messages.success(request, 'Note added successfully!')
        
        if request.headers.get('HX-Request'):
            context = {'claim': claim}
            return render(request, 'claims/claim_notes_partial.html', context)
    else:
        messages.error(request, 'Note content cannot be empty.')
    
    return redirect('claim_detail', claim_id=claim_id)

@login_required
def admin_dashboard(request):
    """Admin dashboard with claim statistics"""
    total_claims = Claim.objects.count()
    flagged_claims = ClaimFlag.objects.values('claim').distinct().count()
    
    status_stats = Claim.objects.values('status').annotate(
        count=Count('id'),
        avg_underpayment=Avg('billed_amount') - Avg('paid_amount'),
        total_billed=Sum('billed_amount'),
        total_paid=Sum('paid_amount')
    ).order_by('status')
    
    recent_flags = ClaimFlag.objects.select_related('claim', 'user').order_by('-flagged_at')[:10]
    
    insurer_stats = Claim.objects.values('insurer_name').annotate(
        claim_count=Count('id'),
        avg_underpayment=Avg('billed_amount') - Avg('paid_amount')
    ).order_by('-claim_count')[:5]
    
    total_notes = ClaimNote.objects.count()
    total_users = User.objects.count()
    
    context = {
        'total_claims': total_claims,
        'flagged_claims': flagged_claims,
        'flag_rate': (flagged_claims / total_claims * 100) if total_claims > 0 else 0,
        'status_stats': status_stats,
        'recent_flags': recent_flags,
        'insurer_stats': insurer_stats,
        'total_notes': total_notes,
        'total_users': total_users,
    }
    
    return render(request, 'claims/admin_dashboard_modern.html', context)
