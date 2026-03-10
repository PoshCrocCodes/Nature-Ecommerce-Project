"""
Management command to seed the database with demo data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from products.models import Category, Product, Review
from core.models import CompanyInfo, FAQItem


class Command(BaseCommand):
    help = "Seed the database with demo categories, products, and info"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding demo data...")

        # Categories
        cats = [
            ("Dairy & Eggs", "🥛", "Fresh milk, cheese, butter, and free-range eggs from local farms."),
            ("Vegetables", "🥕", "Seasonal and organic vegetables harvested fresh."),
            ("Fruit", "🍎", "Locally grown fruits and berries."),
            ("Bakery", "🍞", "Freshly baked bread, pastries, and cakes."),
            ("Meat & Poultry", "🥩", "Ethically reared meats from local farms."),
            ("Honey & Preserves", "🍯", "Raw honey, jams, chutneys, and pickles."),
            ("Drinks", "🧃", "Fresh juices, ciders, and herbal infusions."),
            ("Herbs & Greens", "🌿", "Fresh cut herbs and salad greens."),
        ]
        category_objs = {}
        for i, (name, icon, desc) in enumerate(cats):
            cat, _ = Category.objects.get_or_create(name=name, defaults={"icon": icon, "description": desc, "order": i})
            category_objs[name] = cat

        # Producer account
        producer, created = User.objects.get_or_create(username="demo_producer", defaults={
            "email": "producer@greenfield.test", "first_name": "Jane", "last_name": "Farmer"
        })
        if created:
            producer.set_password("GreenField2024!")
            producer.save()
        profile = producer.profile
        profile.role = "producer"
        profile.farm_name = "Hillside Family Farm"
        profile.bio = "Three generations of sustainable farming in the Greenfield valley."
        profile.save()

        # Consumer account
        consumer, created = User.objects.get_or_create(username="demo_consumer", defaults={
            "email": "consumer@greenfield.test", "first_name": "Tom", "last_name": "Smith"
        })
        if created:
            consumer.set_password("GreenField2024!")
            consumer.save()

        # Products
        products_data = [
            ("Whole Milk (2L)", "Fresh whole milk from grass-fed Friesian cows. Unhomogenised and full of natural goodness.", 1.89, 50, "litre", "Dairy & Eggs", True, True),
            ("Free Range Eggs (Dozen)", "Large free-range eggs from our happy hens roaming the hillside pastures.", 3.49, 30, "dozen", "Dairy & Eggs", False, True),
            ("Farmhouse Cheddar (400g)", "Aged 12 months in our traditional stone cellar. Sharp, crumbly, and full of flavour.", 4.99, 20, "each", "Dairy & Eggs", True, True),
            ("Seasonal Veg Box", "A curated selection of whatever's freshest in our fields this week.", 9.99, 15, "box", "Vegetables", True, True),
            ("Heritage Carrots (1kg)", "Rainbow mix of heritage carrot varieties — sweet, earthy, and naturally organic.", 1.49, 40, "kg", "Vegetables", True, False),
            ("Sourdough Loaf", "Long-fermented sourdough baked fresh every morning using our century-old starter.", 4.25, 12, "each", "Bakery", False, True),
            ("Wildflower Honey (340g)", "Raw, unfiltered honey from our hillside hives. Light and floral with summer wildflower notes.", 6.50, 25, "jar", "Honey & Preserves", True, True),
            ("Strawberry Jam (300g)", "Made from Greenfield strawberries with just a touch of lemon. No artificial additives.", 3.75, 18, "jar", "Honey & Preserves", True, False),
        ]
        product_objs = []
        for name, desc, price, stock, unit, cat_name, is_organic, is_featured in products_data:
            prod, _ = Product.objects.get_or_create(name=name, defaults={
                "description": desc, "price": price, "stock": stock,
                "unit": unit, "category": category_objs.get(cat_name),
                "producer": producer, "is_organic": is_organic, "is_featured": is_featured, "is_active": True
            })
            product_objs.append(prod)

        # Reviews
        review_data = [
            (product_objs[0], consumer, 5, "Best milk I've tasted!", "Incredibly fresh — you can really taste the difference from supermarket milk. Will be ordering weekly!"),
            (product_objs[2], consumer, 5, "Exceptional cheddar", "Rich, crumbly, and perfectly aged. Far better than anything you'll find in a supermarket."),
            (product_objs[3], consumer, 4, "Great value", "Really impressed with the variety in the veg box this week. Everything was beautifully fresh."),
            (product_objs[6], consumer, 5, "Pure liquid gold!", "This honey is absolutely gorgeous. I put it on everything now. The floral notes are incredible."),
        ]
        for product, user, rating, title, comment in review_data:
            Review.objects.get_or_create(product=product, user=user, defaults={
                "rating": rating, "title": title, "comment": comment, "is_approved": True
            })

        # Company info
        info_sections = [
            ("about", "About Greenfield Local Hub", "A cooperative connecting farms and communities",
             "This is a placeholder for the About Greenfield section. Replace this text with your actual company overview, history, and mission. Greenfield Local Hub is a cooperative organisation established to support local farmers and food producers in the region. We operate a single retail outlet and collectively market products from our member producers."),
            ("mission", "Our Mission", "Fresh. Local. Sustainable.",
             "This is a placeholder for the Mission section. Replace with Greenfield's actual mission statement, goals, and values. Our aim is to create a fair, transparent marketplace that benefits both producers and consumers whilst promoting sustainable farming practices."),
            ("how_it_works", "How It Works", "From field to your door in 24 hours",
             "This is a placeholder for the How It Works section. Replace with your actual process description. Producers list their available stock each morning, customers order by midday, and deliveries are made the following day using our refrigerated fleet."),
        ]
        for i, (section, title, subtitle, content) in enumerate(info_sections):
            CompanyInfo.objects.get_or_create(section=section, defaults={
                "title": title, "subtitle": subtitle, "content": content, "order": i, "is_active": True
            })

        # FAQs
        faqs = [
            ("Where does the produce come from?", "All products on Greenfield Local Hub come from farms within 30 miles of our distribution centre. Every producer is vetted and visited personally by our team."),
            ("How fresh is the produce?", "Most products are harvested or prepared within 24 hours of your delivery. Our milk, eggs, and baked goods are always next-day fresh."),
            ("How do I become a producer member?", "Register for a producer account and our team will get in touch within 48 hours to discuss your products and complete the onboarding process."),
            ("What is your delivery area?", "We currently deliver within a 15-mile radius of Greenfield. Click & Collect is available at our hub daily from 8am to 6pm."),
        ]
        for i, (q, a) in enumerate(faqs):
            FAQItem.objects.get_or_create(question=q, defaults={"answer": a, "order": i, "is_active": True})

        self.stdout.write(self.style.SUCCESS("✅ Demo data seeded successfully!"))
        self.stdout.write("   Producer login: demo_producer / GreenField2024!")
        self.stdout.write("   Consumer login: demo_consumer / GreenField2024!")
