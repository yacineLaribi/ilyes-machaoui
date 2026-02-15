from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'rating', 'get_star_display', 'created_at', 'is_read']
    list_filter = ['rating', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations Client', {
            'fields': ('name', 'email')
        }),
        ('Feedback', {
            'fields': ('rating', 'message')
        }),
        ('Statut', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def get_star_display(self, obj):
        """Display star rating in admin"""
        return obj.get_star_display()
    get_star_display.short_description = 'Étoiles'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Mark selected feedbacks as read"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} feedback(s) marqué(s) comme lu(s).')
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected feedbacks as unread"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} feedback(s) marqué(s) comme non lu(s).')
    mark_as_unread.short_description = "Marquer comme non lu"