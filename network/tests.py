from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Contact, NetworkNode, Product


class ContactModelTest(TestCase):
    """Тесты для модели Contact"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.contact = Contact.objects.create(
            email="test@test.com",
            country="Россия",
            city="Москва",
            street="Ленина",
            house_number="15",
        )

    def test_contact_creation(self):
        """Тест создания контакта"""
        self.assertEqual(self.contact.email, "test@test.com")
        self.assertEqual(self.contact.country, "Россия")
        self.assertEqual(self.contact.city, "Москва")
        self.assertEqual(self.contact.street, "Ленина")
        self.assertEqual(self.contact.house_number, "15")

    def test_contact_str_method(self):
        """Тест строкового представления"""
        expected = "Россия, Москва, Ленина 15"
        self.assertEqual(str(self.contact), expected)

    def test_contact_verbose_name(self):
        """Тест verbose_name полей"""
        self.assertEqual(Contact._meta.get_field("email").verbose_name, "Email")
        self.assertEqual(Contact._meta.get_field("country").verbose_name, "Страна")
        self.assertEqual(Contact._meta.get_field("city").verbose_name, "Город")
        self.assertEqual(Contact._meta.get_field("street").verbose_name, "Улица")
        self.assertEqual(
            Contact._meta.get_field("house_number").verbose_name, "Номер дома"
        )


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.product = Product.objects.create(
            name="Смартфон", model="Galaxy S25", release_date="2025-11-01"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Смартфон")
        self.assertEqual(self.product.model, "Galaxy S25")
        self.assertEqual(self.product.release_date, "2025-11-01")

    def test_product_str_method(self):
        """Тест строкового представления"""
        expected = "Смартфон Galaxy S25"
        self.assertEqual(str(self.product), expected)

    def test_product_ordering(self):
        """Тест сортировки по имени"""
        product2 = Product.objects.create(
            name="Телевизор", model="Sony R300", release_date="2025-12-05"
        )
        products = Product.objects.all()
        self.assertEqual(products[0].name, "Смартфон")
        self.assertEqual(products[1].name, "Телевизор")
        self.assertEqual(product2.model, "Sony R300")


class NetworkNodeModelTest(TestCase):
    """Тесты для модели NetworkNode"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создание контактов
        self.contact1 = Contact.objects.create(
            email="factory@test.com",
            country="Корея",
            city="Сеул",
            street="Техно",
            house_number="1",
        )

        self.contact2 = Contact.objects.create(
            email="retail@test.com",
            country="Россия",
            city="Москва",
            street="Тверская",
            house_number="10",
        )

        self.contact3 = Contact.objects.create(
            email="ip@test.com",
            country="Россия",
            city="Тверь",
            street="Центральная",
            house_number="5",
        )

        # создание продукта
        self.product1 = Product.objects.create(
            name="Смартфон", model="Galaxy S25", release_date="2025-11-01"
        )

        self.product2 = Product.objects.create(
            name="Ноутбук", model="Gram", release_date="2026-02-20"
        )

        # Создание узлов сети
        self.factory = NetworkNode.objects.create(
            name="Samsung", node_type=0, contact=self.contact1, debt=Decimal("0.00")
        )

        self.retailer = NetworkNode.objects.create(
            name="М.Видео",
            node_type=1,
            contact=self.contact2,
            supplier=self.factory,
            debt=Decimal("50000.00"),
        )

        self.ip = NetworkNode.objects.create(
            name="ИП Иванов",
            node_type=2,
            contact=self.contact3,
            supplier=self.retailer,
            debt=Decimal("15000.50"),
        )

        # Добавляем продукты к узлам
        self.factory.products.add(self.product1, self.product2)
        self.retailer.products.add(self.product1)
        self.ip.products.add(self.product2)

    def test_node_creation(self):
        """Тест создания узлов"""
        self.assertEqual(self.factory.name, "Samsung")
        self.assertEqual(self.factory.node_type, 0)
        self.assertEqual(self.retailer.name, "М.Видео")
        self.assertEqual(self.retailer.node_type, 1)
        self.assertEqual(self.ip.name, "ИП Иванов")
        self.assertEqual(self.ip.node_type, 2)

    def test_node_str_method(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.factory), "Завод - Samsung")
        self.assertEqual(str(self.retailer), "Розничная сеть - М.Видео")
        self.assertEqual(str(self.ip), "Индивидуальный предприниматель - ИП Иванов")

    def test_node_type_name_property(self):
        """Тест property node_type_name"""
        self.assertEqual(self.factory.node_type_name, "Завод")
        self.assertEqual(self.retailer.node_type_name, "Розничная сеть")
        self.assertEqual(self.ip.node_type_name, "Индивидуальный предприниматель")

    def test_supplier_relationship(self):
        """Тест связей поставщиков"""
        self.assertIsNone(self.factory.supplier)
        self.assertEqual(self.retailer.supplier, self.factory)
        self.assertEqual(self.ip.supplier, self.retailer)

    def test_clients_relationship(self):
        """Тест обратной связи related_name='clients'"""
        self.assertEqual(self.factory.clients.count(), 1)
        self.assertEqual(self.factory.clients.first(), self.retailer)

        self.assertEqual(self.retailer.clients.count(), 1)
        self.assertEqual(self.retailer.clients.first(), self.ip)

        self.assertEqual(self.ip.clients.count(), 0)

    def test_products_relationship(self):
        """Тест связи с продуктами"""
        self.assertEqual(self.factory.products.count(), 2)
        self.assertEqual(self.retailer.products.count(), 1)
        self.assertEqual(self.ip.products.count(), 1)

        self.assertIn(self.product1, self.factory.products.all())
        self.assertIn(self.product2, self.factory.products.all())
        self.assertIn(self.product1, self.retailer.products.all())
        self.assertIn(self.product2, self.ip.products.all())

    def test_debt_field(self):
        """Тест поля задолженности"""
        self.assertEqual(self.factory.debt, Decimal("0.00"))
        self.assertEqual(self.retailer.debt, Decimal("50000.00"))
        self.assertEqual(self.ip.debt, Decimal("15000.50"))

    def test_debt_validation(self):
        """Тест валидации задолженности (не может быть отрицательной)"""
        node = NetworkNode(
            name="Test", node_type=0, contact=self.contact1, debt=Decimal("-100.00")
        )
        with self.assertRaises(ValidationError):
            node.full_clean()  # Запускаем валидацию

    def test_get_hierarchy_level(self):
        """Тест определения уровня иерархии"""
        self.assertEqual(self.factory.get_hierarchy_level(), 0)
        self.assertEqual(self.retailer.get_hierarchy_level(), 1)
        self.assertEqual(self.ip.get_hierarchy_level(), 2)

    def test_hierarchy_level_display(self):
        """Тест отображения уровня иерархии"""
        self.assertEqual(self.factory.hierarchy_level_display, "Завод (уровень 0)")
        self.assertEqual(
            self.retailer.hierarchy_level_display, "Розничная сеть (уровень 1)"
        )
        self.assertEqual(
            self.ip.hierarchy_level_display,
            "Индивидуальный предприниматель (уровень 2)",
        )

    def test_contact_one_to_one(self):
        """Тест связи один-к-одному с контактом"""
        self.assertEqual(self.factory.contact, self.contact1)
        self.assertEqual(self.retailer.contact, self.contact2)
        self.assertEqual(self.ip.contact, self.contact3)

        # Проверяем обратную связь
        self.assertEqual(self.contact1.network_node, self.factory)
        self.assertEqual(self.contact2.network_node, self.retailer)
        self.assertEqual(self.contact3.network_node, self.ip)

    def test_created_at_auto_now_add(self):
        """Тест автоматического заполнения даты создания"""
        self.assertIsNotNone(self.factory.created_at)
        self.assertIsNotNone(self.retailer.created_at)
        self.assertIsNotNone(self.ip.created_at)

    def test_node_ordering(self):
        """Тест сортировки узлов по имени"""
        nodes = NetworkNode.objects.all()
        self.assertEqual(nodes[0].name, "Samsung")  # Должен быть первым по алфавиту
        self.assertEqual(nodes[1].name, "ИП Иванов")
        self.assertEqual(nodes[2].name, "М.Видео")


class NetworkNodeHierarchyTest(TestCase):
    """Дополнительные тесты для иерархии"""

    def test_deep_hierarchy(self):
        """Тест глубокой иерархии (больше 3 уровней)"""
        # Создаем контакты
        contact1 = Contact.objects.create(
            email="c1@test.com", country="РФ", city="Мск", street="ул", house_number="1"
        )
        contact2 = Contact.objects.create(
            email="c2@test.com", country="РФ", city="Мск", street="ул", house_number="2"
        )
        contact3 = Contact.objects.create(
            email="c3@test.com", country="РФ", city="Мск", street="ул", house_number="3"
        )
        contact4 = Contact.objects.create(
            email="c4@test.com", country="РФ", city="Мск", street="ул", house_number="4"
        )

        # Создаем цепочку из 4 уровней
        node1 = NetworkNode.objects.create(
            name="Уровень 0", node_type=0, contact=contact1
        )  # завод
        node2 = NetworkNode.objects.create(
            name="Уровень 1", node_type=1, contact=contact2, supplier=node1
        )
        node3 = NetworkNode.objects.create(
            name="Уровень 2", node_type=2, contact=contact3, supplier=node2
        )
        node4 = NetworkNode.objects.create(
            name="Уровень 3", node_type=2, contact=contact4, supplier=node3
        )

        # Проверяем, что уровень не превышает 2
        self.assertEqual(node1.get_hierarchy_level(), 0)
        self.assertEqual(node2.get_hierarchy_level(), 1)
        self.assertEqual(node3.get_hierarchy_level(), 2)
        self.assertEqual(node4.get_hierarchy_level(), 2)  # Должен быть 2, не 3!

    def test_circular_reference(self):
        """Тест циклических ссылок (не должны создаваться)"""
        contact1 = Contact.objects.create(
            email="c1@test.com", country="РФ", city="Мск", street="ул", house_number="1"
        )
        contact2 = Contact.objects.create(
            email="c2@test.com", country="РФ", city="Мск", street="ул", house_number="2"
        )

        node1 = NetworkNode.objects.create(name="Узел 1", node_type=0, contact=contact1)
        node2 = NetworkNode.objects.create(
            name="Узел 2", node_type=1, contact=contact2, supplier=node1
        )

        # Пытаемся создать циклическую ссылку (узел1 ссылается на узел2)
        node1.supplier = node2
        node1.save()

        # Проверяем, что метод get_hierarchy_level не уходит в бесконечный цикл
        level = node1.get_hierarchy_level()
        self.assertIn(level, [0, 1, 2])  # Должен вернуть какое-то значение без ошибки
