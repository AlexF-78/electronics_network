from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Contact(models.Model):
    """
    Модель контактов для хранения адресной информации звеньев сети.

    Связана с моделью NetworkNode через OneToOneField.
    Каждое звено сети имеет один уникальный контакт.
    Контакт может принадлежать только одному звену сети.
    """

    # Поля модели контакта
    email = models.EmailField(verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house_number = models.CharField(max_length=20, verbose_name="Номер дома")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        """
        Строковое представление контакта.

        Формат: "Страна, Город, Улица Номер_дома"
        Пример: "Россия, Москва, Ленина 15"

        Returns:
            str: Полный адрес контакта
        """
        return f"{self.country}, {self.city}, {self.street} {self.house_number}"


class Product(models.Model):
    """
    Модель продукта, который может продаваться в звеньях сети.

    Продукт может быть связан с несколькими звеньями сети через ManyToManyField.
    Хранит основную информацию о продукте: название, модель и дату выхода.
    """

    name = models.CharField(max_length=100, verbose_name="Название")
    model = models.CharField(max_length=100, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]

    def __str__(self):
        """
        Строковое представление продукта.

        Формат: "Название Модель"
        Пример: "Смартфон Galaxy S25"

        Returns:
            str: Название и модель продукта
        """
        return f"{self.name} {self.model}"


class NetworkNode(models.Model):
    """
    Основная модель звена сети (элемент иерархии поставок).

    Каждое звено имеет:
    - Тип (завод, розничная сеть, ИП)
    - Контактную информацию (OneToOne с Contact)
    - Список продуктов (ManyToMany с Product)
    - Поставщика (ссылку на другой узел)
    - Задолженность перед поставщиком
    - Дату создания

    Иерархия ограничена 3 уровнями:
    - Уровень 0: Завод (нет поставщика)
    - Уровень 1: Розничная сеть (поставщик - завод)
    - Уровень 2: ИП (поставщик - розничная сеть)
    """

    # Типы узлов - константы для выбора в поле node_type
    NODE_TYPES = [
        (0, "Завод"),
        (1, "Розничная сеть"),
        (2, "Индивидуальный предприниматель"),
    ]

    # Основные поля узла
    name = models.CharField(max_length=100, verbose_name="Название")
    node_type = models.IntegerField(
        choices=NODE_TYPES, verbose_name="Тип звена", default=0
    )

    # Связи с другими моделями
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        verbose_name="Контакты",
        related_name="network_node",
    )
    products = models.ManyToManyField(
        Product, verbose_name="Продукты", related_name="network_nodes", blank=True
    )
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Поставщик",
        related_name="clients",
        help_text="Предыдущий по иерархии объект сети",
    )

    # Финансовые поля
    debt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Задолженность перед поставщиком",
        help_text="В денежном выражении (с точностью до копеек)",
    )

    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ["name"]

    def __str__(self):
        """
        Строковое представление звена сети.

        Использует свойство node_type_name для получения текстового типа.
        Формат: "Тип узла - Название"
        Пример: "Завод - Samsung"

        Returns:
            str: Тип и название узла
        """
        return f"{self.node_type_name} - {self.name}"

    @property
    def node_type_name(self):
        """
        Свойство для получения текстового названия типа узла.

        Преобразует числовое значение node_type (0,1,2) в текст
        на основе словаря NODE_TYPES.
        """
        # Получаем числовое значение типа (0, 1 или 2)
        return dict(self.NODE_TYPES)[self.node_type]

    @property
    def hierarchy_level_display(self):
        """
        Свойство для отображения уровня иерархии с пояснением.

        Вычисляет уровень через get_hierarchy_level() и возвращает
        отформатированную строку с типом узла и уровнем.
        """
        # Получаем числовой уровень иерархии (0, 1 или 2)
        level = self.get_hierarchy_level()
        # Предопределенные описания для каждого уровня
        return f"{self.node_type_name} (уровень {level})"

    def get_hierarchy_level(self):
        """
        Определяет уровень узла в иерархии поставок.

        Уровни:
        0 - Завод (нет поставщика)
        1 - Розничная сеть (поставщик - завод)
        2 - ИП (поставщик - розничная сеть)

        Returns:
            int: 0, 1 или 2
        """
        if not self.supplier:
            return 0
        elif not self.supplier.supplier:
            return 1
        else:
            return 2
