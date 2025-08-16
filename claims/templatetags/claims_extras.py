from django import template
from django.utils.safestring import mark_safe
from django.http import QueryDict
import urllib.parse

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split a string by delimiter"""
    if value:
        return value.split(delimiter)
    return []

@register.filter
def div(value, divisor):
    """Divide two numbers"""
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter 
def mul(value, multiplier):
    """Multiply two numbers"""
    try:
        return float(value) * float(multiplier)
    except ValueError:
        return 0

@register.simple_tag
def status_badge(status):
    """Generate status badge with appropriate styling"""
    badges = {
        'Paid': 'badge-success',
        'Denied': 'badge-error', 
        'Under Review': 'badge-warning',
        'Pending': 'badge-info',
    }
    badge_class = badges.get(status, 'badge-info')
    return mark_safe(f'<span class="badge {badge_class}">{status}</span>')

@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    """Replace a single URL parameter while preserving others"""
    request = context['request']
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()

@register.filter 
def get_range(value):
    """Generate range for pagination"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(1, 2)

@register.simple_tag
def pagination_info(page_obj, total_count):
    """Generate pagination information string"""
    if not page_obj.has_other_pages():
        if total_count == 0:
            return "No items"
        elif total_count == 1:
            return "1 item"
        else:
            return f"{total_count} items"
    
    start = page_obj.start_index()
    end = page_obj.end_index()
    
    return f"Showing {start} to {end} of {total_count} items"

@register.filter
def accessibility_label(status):
    """Generate accessibility-friendly labels for status"""
    labels = {
        'Paid': 'Claim status: Paid',
        'Denied': 'Claim status: Denied',
        'Under Review': 'Claim status: Under Review', 
        'Pending': 'Claim status: Pending',
    }
    return labels.get(status, f'Claim status: {status}')

@register.simple_tag
def format_currency(amount):
    """Format currency with accessibility"""
    try:
        formatted = f"${float(amount):,.2f}"
        return mark_safe(f'<span title="{formatted}">{formatted}</span>')
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def make_list(value):
    """Convert string to list of characters for iteration"""
    return list(value)
