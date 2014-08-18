from django.db import models
import datetime

# Create your models here.


class Abstract(models.Model):
    abstract_id = models.IntegerField()
    title = models.TextField(max_length=500)
    abstract_text = models.TextField(max_length = 5000)
    pub_date = models.DateTimeField()

    def __unicode__(self):
        return self.title
