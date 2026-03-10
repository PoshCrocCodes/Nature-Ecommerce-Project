from django import forms
from .models import Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'short_description', 'price', 'stock', 'unit',
                  'category', 'image', 'is_active', 'is_organic', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition', 'rows': 5}),
            'short_description': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition', 'min': '0'}),
            'unit': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 rounded'}),
            'is_organic': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-green-600 rounded'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 rounded'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition', 'placeholder': 'Review title'}),
            'comment': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition', 'rows': 4, 'placeholder': 'Share your experience with this product...'}),
        }
