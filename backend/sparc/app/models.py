from django.db import models

class Order(models.Model):
    PRIORITY_CHOICES=[
        ("low", "Low"),
        ("middle", "Middle"),
        ("high", "High"),
    ]
    
    STATUS_CHOICES = [
        ("not_started", "Not yet started"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]
    
    name = models.CharField(max_length=255)
    order_id = models.IntegerField()
    target_amount = models.IntegerField()
    bill_of_materials = models.FileField(upload_to="bill_of_materials/", null = True, blank = True)
    files = models.FileField(upload_to="files/", null = True, blank = True)
    start_date = models.DateField()
    end_date = models.DateField()
    product_name = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="middle")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    comments = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order_id} - {self.name}"
    
    
class Disruption(models.Model):
    
    name = models.CharField(max_length=255)
    disruption_id = models.IntegerField()
    type = models.CharField(max_length=255)
    ressource = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.disruption_id} - {self.name}"
    
    
class Ressource(models.Model):
    
    name = models.CharField(max_length=255)
    ressource_id = models.IntegerField()
    type = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.ressource_id} - {self.name}"
    

    
    