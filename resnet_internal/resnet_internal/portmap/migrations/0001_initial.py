# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResHallWired',
            fields=[
            ],
            options={
                'verbose_name': 'Residence Halls Wired Port',
                'db_table': 'residence_halls_wired',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
