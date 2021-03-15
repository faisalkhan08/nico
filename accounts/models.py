from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Users(AbstractUser):
    email = models.CharField(max_length=256, blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=256, blank=True, null=True)
    organizational_unit = models.CharField(max_length=256, blank=True, null=True)
    position = models.CharField(max_length=256, blank=True, null=True)

    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.email if self.email else "NA"


class ColorCode(models.Model):
    colour = models.CharField(max_length=256, blank=True, null=True)


class ChartType(models.Model):
    chart = models.CharField(max_length=256, blank=True, null=True)


class ColorSet(models.Model):
    color_set_name = models.CharField(max_length=256, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    chart_type = models.ManyToManyField(ChartType, null=True, blank=True)
    color_code = models.ManyToManyField(ColorCode, null=True, blank=True)


class Templates(models.Model):
    created_by = models.ForeignKey(Users, null=True, blank=True, db_index=True, on_delete=models.CASCADE,
                                   related_name='user_template')
    variable = models.CharField(max_length=256, blank=True, null=True)
    scale_x = models.CharField(max_length=256, blank=True, null=True)
    scale_y = models.CharField(max_length=256, blank=True, null=True)
    scale_step = models.CharField(max_length=256, blank=True, null=True)
    color = models.ForeignKey(ColorSet, null=True, blank=True, db_index=True, on_delete=models.CASCADE,
                              related_name='color_set')
    labeling_title = models.CharField(max_length=256, blank=True, null=True)
    labeling_x = models.CharField(max_length=256, blank=True, null=True)
    labeling_y = models.CharField(max_length=256, blank=True, null=True)
    legends = models.CharField(max_length=256, blank=True, null=True)
    alignment = models.CharField(max_length=256, blank=True, null=True)
    chart_type = models.CharField(max_length=256, blank=True, null=True)
    source_file = models.FileField(upload_to='files/', blank=True, null=True)
