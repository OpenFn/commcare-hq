# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from corehq.sql_db.operations import noop_migration
from corehq.sql_db.operations import RawSQLMigration

migrator = RawSQLMigration(('custom', 'icds_reports', 'migrations', 'sql_templates'))


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports',
         '0022_fix_aggregation'),
    ]

    operations = [
        noop_migration(),
    ]
