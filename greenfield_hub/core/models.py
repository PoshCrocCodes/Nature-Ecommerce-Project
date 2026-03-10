from django.db import models


class CompanyInfo(models.Model):
    SECTION_CHOICES = [
        ('about', 'About Us'),
        ('mission', 'Our Mission'),
        ('history', 'Our History'),
        ('values', 'Our Values'),
        ('how_it_works', 'How It Works'),
        ('contact', 'Contact Information'),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    content = models.TextField(help_text='Main content for this section. This is a placeholder — edit freely.')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"

    class Meta:
        verbose_name = 'Company Info Section'
        verbose_name_plural = 'Company Info Sections'
        ordering = ['order']


class FAQItem(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ Item'
