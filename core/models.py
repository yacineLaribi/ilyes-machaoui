from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    """Model to store customer feedback"""
    
    RATING_CHOICES = [
        (1, 'Décevant'),
        (2, 'Moyen'),
        (3, 'Bien'),
        (4, 'Très bien'),
        (5, 'Excellent'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Évaluation"
    )
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
    
    def __str__(self):
        return f"{self.name} - {self.get_rating_display()} ({self.created_at.strftime('%d/%m/%Y')})"
    
    def get_star_display(self):
        """Returns star icons based on rating"""
        return '⭐' * self.rating