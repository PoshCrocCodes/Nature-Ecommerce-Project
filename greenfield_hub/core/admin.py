from django.contrib import admin
from .models import CompanyInfo, FAQItem


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('section', 'title', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active')


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
