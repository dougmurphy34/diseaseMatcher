from django.db import models
import datetime

# Create your models here.

#Raw data to be classified
class Abstract(models.Model):
    abstract_id = models.IntegerField()
    title = models.TextField(max_length=500)
    abstract_text = models.TextField(max_length=5000)
    pub_date = models.DateTimeField()

    def __unicode__(self):
        return self.title

#users who
class annotator(models.Model):
    username = models.TextField(max_length=25)