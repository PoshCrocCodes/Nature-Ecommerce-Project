from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'subtotal')

    def subtotal(self, obj):
        return f'£{obj.subtotal:.2f}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'user', 'status', 'delivery_method', 'total_price', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'delivery_method', 'created_at')
    search_fields = ('tracking_code', 'user__username', 'user__email')
    readonly_fields = ('tracking_code', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'created_at')

    def item_count(self, obj):
        return obj.item_count

    def total(self, obj):
        return f'£{obj.total:.2f}'
