from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'required': True,
                'placeholder': 'Поделитесь своим опытом работы с нами...'
            }),
            'rating': forms.Select(attrs={'required': True})
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка'
        }