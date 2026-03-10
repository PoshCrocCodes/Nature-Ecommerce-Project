from django.contrib import admin
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'category', 'price', 'stock', 'is_active', 'is_organic', 'created_at')
    list_editable = ('price', 'stock', 'is_active')
    list_filter = ('category', 'is_active', 'is_organic', 'is_featured')
    search_fields = ('name', 'description', 'producer__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'title', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('rating', 'is_approved')
    search_fields = ('user__username', 'product__name', 'comment')
