from django.db import models





class ResourceType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Resource(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.name}"


class DisruptionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Disruption(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(DisruptionType, on_delete=models.CASCADE)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="disruptions",
        null = True,
        blank = True,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    comment = models.CharField(max_length=1023, blank= True, null= True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Worker(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Process(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    work_time = models.TimeField()
    setup_time = models.TimeField()
    workers = models.ManyToManyField(
        Worker,
        related_name="processes",
        blank=True,
    )

    def __str__(self):
        return f"Process {self.id}"


class Order(models.Model):
    name = models.CharField(max_length=255)
    target_amount = models.IntegerField()
    bill_of_materials = models.FileField(upload_to="bill_of_materials/", null=True, blank=True)
    files = models.FileField(upload_to="files/", null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    product_name = models.CharField(max_length=255)
    priority = models.IntegerField()
    status = models.CharField(max_length=20)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    process = models.ManyToManyField(
        Process,
        blank=True
    )

    def __str__(self):
        return f"{self.id} - {self.name}"
