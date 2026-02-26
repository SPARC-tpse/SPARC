from django.db import models
import os

class ResourceType(models.Model):
    name = models.CharField(max_length = 255)

    class Meta:
        db_table = 'sparc_resource_type'

    def __str__(self):
        return f"ResourceType ({self.id}, {self.name})"


class Resource(models.Model):
    name = models.CharField(max_length = 255)
    type = models.ForeignKey(
        ResourceType,
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )
    status = models.IntegerField() # 1 - broken, 2 - in use, 3 - available

    class Meta:
        db_table = 'sparc_resource'

    def __str__(self):
        return f"Resource ({self.id}, {self.name}, {str(self.type)}, {self.status})"


class DisruptionType(models.Model):
    name = models.CharField(max_length = 255)

    class Meta:
        db_table = 'sparc_disruption_type'

    def __str__(self):
        return f"DisruptionType ({self.id}, {self.name})"


class Worker(models.Model):
    name = models.CharField(max_length = 255)

    class Meta:
        db_table = 'sparc_worker'

    def __str__(self):
        return f"Worker ({self.id}, {self.name})"


class Order(models.Model):
    name = models.CharField(max_length = 255)
    order_number = models.IntegerField(
        default=0,
        help_text="Order identifier with syntax: YYYYMMDDxzy"
    )
    target_amount = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    product_name = models.CharField(max_length = 255)
    priority = models.IntegerField() # 1 - High, 2 - Medium, 3 - Low
    status = models.IntegerField()   # 1 - Planned, 2 - Running, 3 - Paused, 4 - Done
    comments = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'sparc_order'

    def __str__(self):
        return f"Order ({self.id}, {self.name}, {self.target_amount}, {self.start_date}, {self.end_date}, {self.product_name}, {self.priority}, {self.status})"


class Process(models.Model):
    name = models.CharField(max_length = 255)
    approximated_time = models.IntegerField(
        default = 0,
        help_text = "The approximated time needed for one pice (in seconds)"
    )
    setup_time = models.IntegerField(
        default = 0,
        help_text = "The time needed to set up the resource (in seconds)"
    )
    waiting_time = models.IntegerField(
        default = 0,
        help_text = "The time before you can access the resource as planed (in seconds)"
    )
    workers = models.ManyToManyField(
        Worker,
        related_name = "processes",
        blank = True,
    )
    resource = models.ForeignKey(
        Resource,
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        null = False,
        blank = False
    )

    class Meta:
        db_table = 'sparc_process'

    def __str__(self):
        return f"Process ({self.id}, {self.name}, {self.setup_time}, {self.waiting_time}, {str(self.workers)}, {str(self.resource)}, {str(self.order)})"


class Disruption(models.Model):
    name = models.CharField(max_length = 255)
    type = models.ForeignKey(
        DisruptionType,
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )
    process = models.ForeignKey(
        Process,
        on_delete = models.SET_NULL,
        null = True,
        blank = True
    )
    resource = models.ForeignKey(
        Resource,
        on_delete = models.SET_NULL,
        related_name = "disruptions",
        null = True,
        blank = True,
    )
    created_at = models.DateTimeField(auto_now_add = True)
    disruption_time = models.IntegerField(
        default = 0,
        help_text = "Disruption time in seconds"
    )

    class Meta:
        db_table = 'sparc_disruption'

    def __str__(self):
        return f"Disruption ({self.id}, {self.name}, {self.type}, {self.process}, {self.resource}, {self.disruption_time})"


def order_file_upload_path(instance, filename):
    """
    Files will be uploaded to:
    - media/{order_id}/bom/{filename} for BOM files
    - media/{order_id}/general/{filename} for general files
    """
    if instance.file_type == 'bom':
        return f'{instance.order.id}/bom/{filename}'
    else:
        return f'{instance.order.id}/general/{filename}'

class OrderFile(models.Model):
    FILE_TYPES = [
        ('bom', 'Bill of Materials'),
        ('general', 'General File'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = 'order_files'
    )
    file = models.FileField(upload_to = order_file_upload_path)
    file_type = models.CharField(max_length = 20, choices = FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = 'sparc_order_file'

    def __str__(self):
        return f"OrderFile ({self.id}, {str(self.order)}, {self.get_filename()}, {self.file_type})"

    def get_filename(self):
        """Extract just the filename from the file path"""
        return os.path.basename(self.file.name)


class Part(models.Model):
    process = models.ForeignKey(
        Process,
        on_delete = models.CASCADE,
        null = False,
        blank = False
    )
    # time to put the material in machine
    #setup_time = models.IntegerField(
    #    default = 0,
    #    help_text = "Setup time in seconds"
    #)
    # the time the machine needs to make the part
    process_time = models.IntegerField(
        default = 0,
        help_text = "Process time in seconds"
    )

    class Meta:
        db_table = 'sparc_part'

    def __str__(self):
        return f"Part ({self.id}, {str(self.process)}, {self.process_time})"
