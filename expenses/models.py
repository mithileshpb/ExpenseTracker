from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='expenses', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255,blank=True)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f'Expense Related to-{self.category}'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.name} - {self.amount}'
