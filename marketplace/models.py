from django.db import models

from accounts.models import User
from menu.models import FoodItem

# Create your models here.
class Cart(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  food_item = models.ForeignKey(FoodItem, related_name='cart_by_food_item', on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.user