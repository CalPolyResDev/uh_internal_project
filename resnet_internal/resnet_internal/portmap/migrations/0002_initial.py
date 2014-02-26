# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        u'portmap.reshallwired': {
            'Meta': {'object_name': 'ResHallWired', 'db_table': "u'residence_halls_wired'", 'managed': 'False'},
            'active': ('django.db.models.fields.BooleanField', [], {}),
            'blade': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'building': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'community': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jack': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'port': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'switch_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'switch_name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'vlan': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        }
    }

    complete_apps = ['portmap']