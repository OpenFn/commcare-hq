# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-01 18:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_sector_datamigration', '0007_auto_20170601_1824'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpisodePrescription',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('adultOrPaediatric', models.CharField(max_length=255, null=True)),
                ('beneficiaryId', models.CharField(db_index=True, max_length=18, null=True)),
                ('creationDate', models.DateTimeField()),
                ('creator', models.CharField(max_length=255, null=True)),
                ('dosageStrength', models.CharField(max_length=255, null=True)),
                ('episodeId', models.CharField(max_length=8, null=True)),
                ('modificationDate', models.DateTimeField(null=True)),
                ('modifiedBy', models.CharField(max_length=255, null=True)),
                ('next_refill_date', models.DateTimeField(null=True)),
                ('numberOfDays', models.IntegerField()),
                ('numberOfDaysPrescribed', models.CharField(max_length=255)),
                ('numberOfRefill', models.CharField(max_length=255, null=True)),
                ('owner', models.CharField(max_length=255, null=True)),
                ('presUnits', models.CharField(max_length=255, null=True)),
                ('prescStatus', models.CharField(max_length=255, null=True)),
                ('prescriptionID', models.IntegerField()),
                ('pricePerUnit', models.DecimalField(decimal_places=10, max_digits=14)),
                ('pricePerUnits', models.CharField(max_length=255, null=True)),
                ('productID', models.IntegerField()),
                ('productName', models.CharField(max_length=255, null=True)),
                ('refill_Index', models.IntegerField()),
                ('typicalUnits', models.CharField(max_length=255, null=True)),
                ('unitDesc', models.CharField(max_length=255, null=True)),
                ('voucherID', models.IntegerField()),
                ('voucherStatus', models.CharField(max_length=255, null=True)),
                ('motechUserName', models.CharField(max_length=255, null=True)),
                ('physicalVoucherNumber', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.BigIntegerField()),
                ('caseId', models.CharField(max_length=18, null=True)),
                ('comments', models.CharField(max_length=512, null=True)),
                ('creationDate', models.DateTimeField()),
                ('creator', models.CharField(max_length=255, null=True)),
                ('episodeId', models.CharField(max_length=8, null=True)),
                ('issuedAmount', models.CharField(max_length=255, null=True)),
                ('labId', models.CharField(max_length=255, null=True)),
                ('labTestId', models.CharField(max_length=255, null=True)),
                ('modificationDate', models.DateTimeField()),
                ('modifiedBy', models.CharField(max_length=255, null=True)),
                ('owner', models.CharField(max_length=255, null=True)),
                ('pharmacyId', models.CharField(max_length=255, null=True)),
                ('prescriptionId', models.CharField(max_length=255, null=True)),
                ('validationModeId', models.CharField(max_length=255, null=True)),
                ('voucherAmount', models.CharField(max_length=255, null=True)),
                ('voucherCreatedDate', models.DateTimeField()),
                ('voucherGeneratedBy', models.CharField(max_length=255, null=True)),
                ('voucherLastUpdateDate', models.DateTimeField(null=True)),
                ('voucherNumber', models.BigIntegerField(primary_key=True, serialize=False)),
                ('voucherStatusId', models.CharField(max_length=255, null=True)),
                ('voucherTypeId', models.CharField(max_length=255, null=True)),
                ('agencyName', models.CharField(max_length=255, null=True)),
                ('voucherCancelledDate', models.DateTimeField(null=True)),
                ('voucherExpiredDate', models.DateTimeField(null=True)),
                ('voucherValidatedDate', models.DateTimeField(null=True)),
                ('voucherUsedDate', models.DateTimeField(null=True)),
                ('physicalVoucherNumber', models.CharField(max_length=255, null=True)),
                ('markedUpVoucherAmount', models.CharField(max_length=255, null=True)),
                ('voucherAmountSystem', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
