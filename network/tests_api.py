from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact, NetworkNode, Product


class APITests(APITestCase):
    """Тесты для API звеньев сети"""

    def setUp(self):
        """подготовка данных для тестов API"""
        # Создаём тестового администратора
        self.admin = User.objects.create_superuser(
            username="admin", password="admin123", email="admin@test.com"
        )

        # Создаём обычного пользователя
        self.user = User.objects.create_user(
            username="user", password="user123", email="user@test.com"
        )

        # Создаём тестовые данные
        self.contact = Contact.objects.create(
            email="test@api.com",
            country="Россия",
            city="Москва",
            street="Тестовая",
            house_number="1",
        )

        self.product = Product.objects.create(
            name="Телефон", model="Test Pro", release_date="2026-01-01"
        )

        self.node = NetworkNode.objects.create(
            name="Тестовый узел",
            node_type=0,
            contact=self.contact,
            debt=Decimal("1000.00"),
        )
        self.node.products.add(self.product)

    def test_api_permission_denied_for_regular_user(self):
        """тест: обычный пользователь не имеет доступа к API"""
        self.client.login(username="user", password="user123")
        response = self.client.get("/api/node/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_permission_granted_for_admin(self):
        """Тест: администратор имеет доступ к API"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/api/node/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_get_list(self):
        """Тест получения списка узлов"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/api/node/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_api_get_detail(self):
        """Тест получения конкретного узла"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(f"/api/node/{self.node.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Тестовый узел")
        self.assertEqual(response.data["debt"], "1000.00")

    def test_api_create_node(self):
        """Тест создания нового узла через API"""
        self.client.login(username="admin", password="admin123")
        # Создаём новый контакт для узла
        new_contact = Contact.objects.create(
            email="new@api.com",
            country="Россия",
            city="СПБ",
            street="Новая",
            house_number="10",
        )
        data = {"name": "Новый узел", "node_type": 1, "contact": new_contact.id}
        response = self.client.post("/api/node/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Новый узел")
        self.assertEqual(response.data["debt"], "0.00")

    def test_api_debt_read_only(self):
        """Тест: поле debt нельзя изменить через API"""
        self.client.login(username="admin", password="admin123")

        # Запоминаем первоначальный долг для проверки
        original_debt = self.node.debt

        # Пытаемся обновить debt
        data = {"debt": "5000.00"}
        response = self.client.patch(f"/api/node/{self.node.id}/", data, format="json")

        # Проверяем что запрос выполнен успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что debt не изменился
        self.node.refresh_from_db()
        self.assertEqual(self.node.debt, original_debt)
        self.assertNotEqual(self.node.debt, Decimal(5000.00))

    def test_api_filter_by_country(self):
        """тест фильтрации по стране"""
        self.client.login(username="admin", password="admin123")
        # создаём узел в другой стране
        usa_contact = Contact.objects.create(
            email="usa@test.com",
            country="USA",
            city="NY",
            street="Broadway",
            house_number="1",
        )
        NetworkNode.objects.create(name="USA Node", node_type=1, contact=usa_contact)
        # фильтруем по "Россия"
        response = self.client.get("/api/node/?contact__country__icontains=Россия")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что все результаты имеют страну Россия
        for node in response.data:
            self.assertEqual(node["contact_detail"]["country"], "Россия")

    def test_api_unauthorized_access(self):
        """Тест доступа без авторизации"""
        response = self.client.get("/api/node/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
