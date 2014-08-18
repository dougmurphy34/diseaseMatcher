# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Abstract'
        db.create_table(u'diseaseMatcherApp_abstract', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abstract_id', self.gf('django.db.models.fields.IntegerField')()),
            ('title', self.gf('django.db.models.fields.TextField')(max_length=5000)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'diseaseMatcherApp', ['Abstract'])


    def backwards(self, orm):
        # Deleting model 'Abstract'
        db.delete_table(u'diseaseMatcherApp_abstract')


    models = {
        u'diseaseMatcherApp.abstract': {
            'Meta': {'object_name': 'Abstract'},
            'abstract_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '5000'})
        }
    }

    complete_apps = ['diseaseMatcherApp']