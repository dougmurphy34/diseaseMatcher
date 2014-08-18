from django.db import models
import datetime
from django.utils import timezone

# Create your models here.

#Raw data to be classified
class Abstract(models.Model):
    abstract_id = models.IntegerField()
    title = models.TextField(max_length=500)
    abstract_text = models.TextField(max_length=5000)
    pub_date = models.DateTimeField()

    def __unicode__(self):
        return self.title

#users
class annotator(models.Model):
    username = models.TextField(max_length=25)
    last_entry_date = models.DateTimeField(default=timezone.now())

    def __unicode__(self):
        return self.username

class unused_temp_class(models.Model):
    string_field = models.TextField(max_length=10)
    number_field = models.IntegerField(default=0)