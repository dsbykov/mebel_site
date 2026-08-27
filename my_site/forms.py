from django import forms
from .image_processing import optimize_portfolio_image
from .models import ProjectImage, Review

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


class ProjectImageAdminForm(forms.ModelForm):
    """Преобразует файл до сохранения и выводит ошибки рядом с полем загрузки."""

    class Meta:
        model = ProjectImage
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image or getattr(image, '_committed', False):
            return image
        return optimize_portfolio_image(image)
