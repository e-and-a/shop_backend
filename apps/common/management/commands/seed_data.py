from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Brand, Category, Favorite, Product
from apps.orders.models import Order
from apps.orders.services import create_order_from_cart
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Create demo users, catalog, reviews and orders for the online tech store."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        admin = self.create_user(
            User,
            email="admin@example.com",
            password="admin12345",
            role=User.Roles.ADMIN,
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=True,
        )
        manager = self.create_user(
            User,
            email="manager@example.com",
            password="manager12345",
            role=User.Roles.MANAGER,
            first_name="Manager",
            last_name="User",
            is_staff=True,
        )
        customer = self.create_user(
            User,
            email="customer@example.com",
            password="customer12345",
            role=User.Roles.CUSTOMER,
            first_name="Customer",
            last_name="User",
            phone="+79990000000",
        )

        categories = self.create_categories()
        brands = self.create_brands()
        products = self.create_products(categories, brands, manager)
        self.create_demo_order(customer, products)
        self.create_reviews(customer, products)
        self.create_favorites(customer, products)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("Users:")
        self.stdout.write("  admin@example.com / admin12345")
        self.stdout.write("  manager@example.com / manager12345")
        self.stdout.write("  customer@example.com / customer12345")

    def create_user(self, User, email, password, **defaults):
        user, created = User.objects.get_or_create(email=email, defaults=defaults)
        for field, value in defaults.items():
            setattr(user, field, value)
        user.set_password(password)
        user.save()
        return user

    def create_categories(self):
        data = [
            ("Смартфоны", "smartphones", "Смартфоны и мобильные устройства."),
            ("Ноутбуки", "laptops", "Ноутбуки для работы, учебы и игр."),
            ("Планшеты", "tablets", "Планшеты и аксессуары."),
            ("Мониторы", "monitors", "Мониторы для дома и офиса."),
            ("Комплектующие", "components", "Комплектующие для ПК."),
            ("Периферия", "peripherals", "Клавиатуры, мыши и гарнитуры."),
            ("Бытовая техника", "home-appliances", "Техника для дома."),
        ]
        return {
            slug: Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "is_active": True},
            )[0]
            for name, slug, description in data
        }

    def create_brands(self):
        data = [
            ("Apple", "apple", "USA"),
            ("Samsung", "samsung", "South Korea"),
            ("Lenovo", "lenovo", "China"),
            ("ASUS", "asus", "Taiwan"),
            ("Acer", "acer", "Taiwan"),
            ("Xiaomi", "xiaomi", "China"),
            ("LG", "lg", "South Korea"),
            ("Sony", "sony", "Japan"),
        ]
        return {
            slug: Brand.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "country": country, "description": f"{name} electronics.", "is_active": True},
            )[0]
            for name, slug, country in data
        }

    def create_products(self, categories, brands, manager):
        data = [
            {
                "category": "smartphones",
                "brand": "apple",
                "title": "Apple iPhone 15 128GB",
                "slug": "apple-iphone-15-128gb",
                "sku": "PHONE-APL-15-128",
                "price": Decimal("84990.00"),
                "old_price": Decimal("89990.00"),
                "stock": 15,
                "warranty_months": 12,
                "description": "Смартфон Apple с OLED-дисплеем и камерой 48 Мп.",
                "characteristics": {
                    "screen_size": "6.1",
                    "memory": "128GB",
                    "camera": "48MP",
                    "battery_capacity": "3349mAh",
                },
            },
            {
                "category": "smartphones",
                "brand": "samsung",
                "title": "Samsung Galaxy S24 256GB",
                "slug": "samsung-galaxy-s24-256gb",
                "sku": "PHONE-SAM-S24-256",
                "price": Decimal("79990.00"),
                "old_price": Decimal("84990.00"),
                "stock": 12,
                "warranty_months": 12,
                "description": "Флагманский смартфон Samsung с AMOLED-экраном.",
                "characteristics": {
                    "screen_size": "6.2",
                    "memory": "256GB",
                    "camera": "50MP",
                    "battery_capacity": "4000mAh",
                },
            },
            {
                "category": "laptops",
                "brand": "lenovo",
                "title": "Lenovo IdeaPad Slim 5",
                "slug": "lenovo-ideapad-slim-5",
                "sku": "LAP-LEN-SLIM5",
                "price": Decimal("64990.00"),
                "old_price": Decimal("69990.00"),
                "stock": 8,
                "warranty_months": 24,
                "description": "Универсальный ноутбук для работы и учебы.",
                "characteristics": {
                    "processor": "AMD Ryzen 5",
                    "ram": "16GB",
                    "storage": "512GB SSD",
                    "screen_size": "14",
                    "gpu": "Integrated",
                },
            },
            {
                "category": "laptops",
                "brand": "asus",
                "title": "ASUS TUF Gaming F15",
                "slug": "asus-tuf-gaming-f15",
                "sku": "LAP-ASUS-TUF-F15",
                "price": Decimal("109990.00"),
                "old_price": Decimal("119990.00"),
                "stock": 5,
                "warranty_months": 24,
                "description": "Игровой ноутбук с дискретной графикой.",
                "characteristics": {
                    "processor": "Intel Core i7",
                    "ram": "16GB",
                    "storage": "1TB SSD",
                    "screen_size": "15.6",
                    "gpu": "NVIDIA RTX 4060",
                },
            },
            {
                "category": "tablets",
                "brand": "xiaomi",
                "title": "Xiaomi Pad 6 128GB",
                "slug": "xiaomi-pad-6-128gb",
                "sku": "TAB-XIA-PAD6-128",
                "price": Decimal("32990.00"),
                "old_price": None,
                "stock": 20,
                "warranty_months": 12,
                "description": "Планшет с ярким экраном и металлическим корпусом.",
                "characteristics": {"screen_size": "11", "memory": "128GB", "battery_capacity": "8840mAh"},
            },
            {
                "category": "monitors",
                "brand": "lg",
                "title": "LG UltraGear 27GP850",
                "slug": "lg-ultragear-27gp850",
                "sku": "MON-LG-27GP850",
                "price": Decimal("39990.00"),
                "old_price": Decimal("44990.00"),
                "stock": 7,
                "warranty_months": 36,
                "description": "Игровой монитор с высокой частотой обновления.",
                "characteristics": {
                    "diagonal": "27",
                    "resolution": "2560x1440",
                    "refresh_rate": "165Hz",
                    "matrix_type": "Nano IPS",
                },
            },
            {
                "category": "components",
                "brand": "acer",
                "title": "Acer Predator GM7000 1TB SSD",
                "slug": "acer-predator-gm7000-1tb-ssd",
                "sku": "SSD-ACER-GM7000-1TB",
                "price": Decimal("9990.00"),
                "old_price": None,
                "stock": 30,
                "warranty_months": 60,
                "description": "Высокоскоростной NVMe SSD для ПК и ноутбуков.",
                "characteristics": {"storage": "1TB", "interface": "PCIe 4.0", "read_speed": "7400MB/s"},
            },
            {
                "category": "peripherals",
                "brand": "sony",
                "title": "Sony WH-1000XM5",
                "slug": "sony-wh-1000xm5",
                "sku": "AUD-SONY-WH1000XM5",
                "price": Decimal("34990.00"),
                "old_price": Decimal("37990.00"),
                "stock": 10,
                "warranty_months": 12,
                "description": "Беспроводные наушники с активным шумоподавлением.",
                "characteristics": {"type": "wireless headphones", "battery_life": "30h", "noise_cancelling": True},
            },
            {
                "category": "home-appliances",
                "brand": "samsung",
                "title": "Samsung Bespoke Microwave",
                "slug": "samsung-bespoke-microwave",
                "sku": "HOME-SAM-MW-BSPK",
                "price": Decimal("21990.00"),
                "old_price": None,
                "stock": 4,
                "warranty_months": 24,
                "description": "Микроволновая печь для современной кухни.",
                "characteristics": {"volume": "23L", "power": "800W", "control": "touch"},
            },
        ]

        products = {}
        for item in data:
            category = categories[item.pop("category")]
            brand = brands[item.pop("brand")]
            sku = item["sku"]
            product, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    **item,
                    "category": category,
                    "brand": brand,
                    "created_by": manager,
                    "is_active": True,
                },
            )
            products[sku] = product
        return products

    def create_demo_order(self, customer, products):
        if Order.objects.filter(user=customer, comment="Seed demo completed order").exists():
            return
        cart, _ = Cart.objects.get_or_create(user=customer)
        cart.items.all().delete()
        for sku, quantity in (
            ("PHONE-APL-15-128", 1),
            ("LAP-LEN-SLIM5", 1),
            ("AUD-SONY-WH1000XM5", 2),
        ):
            CartItem.objects.create(cart=cart, product=products[sku], quantity=quantity)
        order = create_order_from_cart(
            user=customer,
            delivery_address="Москва, ул. Тверская, д. 1",
            phone="+79990000000",
            comment="Seed demo completed order",
        )
        order.status = Order.Status.COMPLETED
        order.save(update_fields=("status", "updated_at"))

    def create_reviews(self, customer, products):
        reviews = [
            ("PHONE-APL-15-128", 5, "Отличный смартфон, быстрая работа и хорошая камера."),
            ("LAP-LEN-SLIM5", 4, "Хороший ноутбук для учебы и офисных задач."),
            ("AUD-SONY-WH1000XM5", 5, "Качественный звук и эффективное шумоподавление."),
        ]
        for sku, rating, text in reviews:
            Review.objects.update_or_create(
                product=products[sku],
                user=customer,
                defaults={"rating": rating, "text": text, "is_moderated": True},
            )

    def create_favorites(self, customer, products):
        for sku in ("PHONE-APL-15-128", "PHONE-SAM-S24-256"):
            product = products[sku]
            Favorite.objects.get_or_create(user=customer, product=product)
