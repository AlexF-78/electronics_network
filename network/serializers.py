from rest_framework import serializers

from .models import Contact, NetworkNode, Product


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для контактов"""

    class Meta:
        model = Contact
        fields = ["id", "email", "country", "city", "street", "house_number"]


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктов"""

    class Meta:
        model = Product
        fields = ["id", "name", "model", "release_date"]


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для звеньев"""

    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), help_text="Выберите контакта"
    )
    contact_detail = ContactSerializer(source="contact", read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=NetworkNode.objects.all(),
        required=False,
        allow_null=True,
        help_text="Выберите поставщика",
    )
    supplier_detail = serializers.StringRelatedField(source="supplier", read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            "id",
            "name",
            "node_type",
            "contact",
            "contact_detail",
            "products",
            "supplier",
            "supplier_detail",
            "debt",
            "created_at",
        ]
        read_only_fields = ["debt"]
