from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from .models import Contact, NetworkNode, Product


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Настройка отображения контактов в админке"""

    list_display = ("email", "country", "city", "street", "house_number")
    list_filter = ("country", "city")
    search_fields = ("email", "country", "city")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка отображение продуктов в админке"""

    list_display = ("name", "model", "release_date")
    list_filter = ("name",)
    search_fields = ("name", "model")
    date_hierarchy = "release_date"


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    """Настройки отображения звеньев сети в административной панели."""

    list_display = (
        "name",
        "node_type",
        "get_city",
        "supplier_link",
        "debt",
        "created_at",
    )
    list_filter = ("node_type", "contact__city")
    search_fields = ("name", "contact__city")
    readonly_fields = ("created_at",)
    actions = ["clear_debt"]

    def get_city(self, obj):
        """Получаем город из связанного контакта"""
        # Если контакта нет возвращает '-'
        if not obj.contact or not obj.contact.city:
            return "-"

        # Если контакт есть, получаем город
        return obj.contact.city

    get_city.short_description = "Город"
    get_city.admin_order_field = "contact__city"

    def supplier_link(self, obj):
        if not obj.supplier:
            return "-"

        url = reverse("admin:network_networknode_change", args=[obj.supplier.id])
        return format_html('<a href="{}">{}</a>', url, obj.supplier.name)

    supplier_link.short_description = "Поставщик"
    supplier_link.admin_order_field = "supplier__name"

    def clear_debt(self, request, queryset):
        """Admin action для очистки задолженности (только для суперпользователей)"""
        if not request.user.is_superuser:
            self.message_user(
                request, "Только администратор может очищать долг", messages.ERROR
            )
            return None

        updated = queryset.update(debt=0)
        self.message_user(
            request, f"У {updated} звеньев задолженность очищена", messages.SUCCESS
        )

    clear_debt.short_description = "Очистить задолженность перед поставщиком"
