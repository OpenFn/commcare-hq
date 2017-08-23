import csv
import os
import re
from decimal import Decimal

import six
import sqlalchemy
from datetime import datetime, date, time
from django.db import connections
from django.test.testcases import TransactionTestCase
import postgres_copy

from corehq.sql_db.connections import connection_manager
from custom.icds_reports.tasks import move_ucr_data_into_aggregation_tables

FILE_NAME_TO_TABLE_MAPPING = {
    'awc_mgmt': 'config_report_icds-cas_static-awc_mgt_forms_ad1b11f0',
    'ccs_cases': 'config_report_icds-cas_static-ccs_record_cases_cedcca39',
    'ccs_monthly': 'config_report_icds-cas_static-ccs_record_cases_monthly_33021c88',
    'child_cases': 'config_report_icds-cas_static-child_health_cases_a46c129f',
    'child_monthly': 'config_report_icds-cas_static-child_cases_monthly_tabl_d4032f37',
    'daily_feeding': 'config_report_icds-cas_static-daily_feeding_forms_85b1167f',
    'household_cases': 'household_cases',
    'infrastructure': 'config_report_icds-cas_static-infrastructure_form_05fe0f1a',
    'location_ucr': 'config_report_icds-cas_static-awc_location_88b3f9c3',
    'person_cases': 'person_cases',
    'ucr_table_name_mapping': 'ucr_table_name_mapping',
    'usage': 'config_report_icds-cas_static-usage_forms_92fbe2aa',
    'vhnd': 'config_report_icds-cas_static-vhnd_form_28e7fd58'
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'outputs')


class AggregationScriptTest(TransactionTestCase):

    def _load_csv(self, path):
        with open(path) as f:
            csv_data = list(csv.reader(f))
            headers = csv_data[0]
            for row_count, row in enumerate(csv_data):
                for idx, value in enumerate(row):
                    if value == '':
                        row[idx] = 'None'
                csv_data[row_count] = dict(zip(headers, row))
        return csv_data[1:]

    def _convert_decimal_to_string(self, value):
        """
            Args:
                value (decimal.Decimal)
            Returns:
                str
            Converts scientific notation to decimal form if needed.
            it's needed because in csv file all numbers are written in decimal form.
            Here is an example why we can't simply apply str to decimal number
                >>> str(Decimal('0.0000000'))
                '0E-7'
                >>> self._convert_decimal_to_string(Decimal('0.0000000'))
                '0.0000000'
        """
        value_str = str(value)
        p = re.compile('0E-(?P<zeros>[0-9]+)')
        match = p.match(value_str)
        if match:
            return '0.{}'.format(int(match.group('zeros')) * '0')
        else:
            return value_str

    def _load_data_from_db(self, table_name):
        engine = connection_manager.get_session_helper('default').engine
        metadata = sqlalchemy.MetaData(bind=engine, reflect=True)
        table = metadata.tables[table_name]
        columns = [
            column.name
            for column in table.columns
        ]
        with engine.begin() as connection:
            for row in list(connection.execute(table.select())):
                row = list(row)
                for idx, value in enumerate(row):
                    if isinstance(value, date):
                        row[idx] = value.strftime('%Y-%m-%d')
                    elif isinstance(value, time):
                        row[idx] = value.strftime("%H:%M:%S.%f").rstrip('0')
                    elif isinstance(value, six.integer_types):
                        row[idx] = str(value)
                    elif isinstance(value, (float, Decimal)):
                        row[idx] = self._convert_decimal_to_string(row[idx])
                    elif isinstance(value, basestring):
                        row[idx] = value.encode('utf-8')
                    elif value is None:
                        row[idx] = 'None'
                yield dict(zip(columns, row))

    def _fasterAssertListEqual(self, list1, list2):
        if len(list1) != len(list2):
            self.fail('Lists are not equal')

        messages = []

        for idx in range(len(list1)):
            dict1 = list1[idx]
            dict2 = list2[idx]

            differences = []

            for key in dict1.keys():
                value1 = dict1[key]
                value2 = dict2[key]
                if value1 != value2:
                    differences.append(key)

            if differences:
                messages.append("""
                    Actual and expected row {} are not the same
                    Actual:   {}
                    Expected: {} 
                """.format(
                    idx + 1,
                    ', '.join(['{}: {}'.format(difference, dict1[difference]) for difference in differences]),
                    ', '.join(['{}: {}'.format(difference, dict2[difference]) for difference in differences])
                ))

        if messages:
            self.fail('\n'.join(messages))

    def _load_and_compare_data(self, table_name, path, sort_key=None):
        sort_key = sort_key or (lambda x: x)
        self._fasterAssertListEqual(
            sorted(
                list(self._load_data_from_db(table_name)),
                key=sort_key
            ),
            sorted(
                self._load_csv(path),
                key=sort_key
            )
        )

    @classmethod
    def setUpTestData(cls):
        engine = connection_manager.get_session_helper('default').engine
        metadata = sqlalchemy.MetaData(bind=engine, reflect=True)
        path = os.path.join(os.path.dirname(__file__), 'fixtures')
        for file_name in os.listdir(path):
            with open(os.path.join(path, file_name)) as f:
                table_name = FILE_NAME_TO_TABLE_MAPPING[file_name[:-4]]
                table = metadata.tables[table_name]
                csv_data = [row for row in csv.DictReader(f) if 'doc_id' not in row or row['doc_id']]
                for row in csv_data:
                    for key, value in six.iteritems(row):
                        if value == '':
                            row[key] = None
                postgres_copy.copy_from(f, table, engine, format='csv', null='', header=True)

                with engine.begin() as connection:
                    connection.execute(table.insert().values(csv_data))

    @classmethod
    def setUpClass(cls):
        super(AggregationScriptTest, cls).setUpClass()
        connection = connections['default']
        with connection.cursor() as cursor:
            path = os.path.join(os.path.dirname(__file__), 'sql_templates', 'generate_tables.sql')
            with open(path, "r") as sql_file:
                sql_to_execute = ' '.join(sql_file.readlines()).strip()
                for sql in sql_to_execute.split(';'):
                    if not sql:
                        continue
                    cursor.execute(sql)
        cls.setUpTestData()
        move_ucr_data_into_aggregation_tables(datetime(2017, 5, 28), intervals=2)

    def test_awc_location(self):
        self._load_and_compare_data(
            'awc_location',
            os.path.join(OUTPUT_PATH, 'awc_location.csv'),
            sort_key=lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['doc_id'])
        )

    def test_icds_months(self):
        self._load_and_compare_data(
            'icds_months',
            os.path.join(OUTPUT_PATH, 'icds_months.csv'),
            sort_key=lambda x: x['month_name']
        )

    def test_ccs_record_monthly_2017_04_01(self):
        self._load_and_compare_data(
            'ccs_record_monthly_2017-04-01',
            os.path.join(OUTPUT_PATH, 'ccs_record_monthly_2017-04-01.csv'),
            sort_key=lambda x: (x['awc_id'], x['case_id'])
        )

    def test_ccs_record_monthly_2017_05_01(self):
        self._load_and_compare_data(
            'ccs_record_monthly_2017-05-01',
            os.path.join(OUTPUT_PATH, 'ccs_record_monthly_2017-05-01.csv'),
            sort_key=lambda x: (x['awc_id'], x['case_id'])
        )
        
    def test_daily_attendance_2017_04_01(self):
        self._load_and_compare_data(
            'daily_attendance_2017-04-01',
            os.path.join(OUTPUT_PATH, 'daily_attendance_2017-04-01.csv'),
            sort_key=lambda x: (x['awc_id'], x['doc_id'])
        )

    def test_daily_attendance_2017_05_01(self):
        self._load_and_compare_data(
            'daily_attendance_2017-05-01',
            os.path.join(OUTPUT_PATH, 'daily_attendance_2017-05-01.csv'),
            sort_key=lambda x: (x['awc_id'], x['doc_id'])
        )
        
    def test_child_health_monthly_2017_04_01(self):
        self._load_and_compare_data(
            'child_health_monthly_2017-04-01',
            os.path.join(OUTPUT_PATH, 'child_health_monthly_2017-04-01.csv')
        )

    def test_child_health_monthly_2017_05_01(self):
        self._load_and_compare_data(
            'child_health_monthly_2017-05-01',
            os.path.join(OUTPUT_PATH, 'child_health_monthly_2017-05-01.csv')
        )

    def test_agg_awc_daily(self):
        self._load_and_compare_data(
            'agg_awc_daily_2017-05-28',
            os.path.join(OUTPUT_PATH, 'agg_awc_daily_2017-05-28.csv'),
            sort_key=lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_04_01_1(self):
        self._load_and_compare_data(
            'agg_awc_2017-04-01_1',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-04-01_1.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_04_01_2(self):
        self._load_and_compare_data(
            'agg_awc_2017-04-01_2',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-04-01_2.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_04_01_3(self):
        self._load_and_compare_data(
            'agg_awc_2017-04-01_3',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-04-01_3.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_04_01_4(self):
        self._load_and_compare_data(
            'agg_awc_2017-04-01_4',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-04-01_4.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_04_01_5(self):
        self._load_and_compare_data(
            'agg_awc_2017-04-01_5',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-04-01_5.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_05_01_1(self):
        self._load_and_compare_data(
            'agg_awc_2017-05-01_1',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-05-01_1.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_05_01_2(self):
        self._load_and_compare_data(
            'agg_awc_2017-05-01_2',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-05-01_2.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_05_01_3(self):
        self._load_and_compare_data(
            'agg_awc_2017-05-01_3',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-05-01_3.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_05_01_4(self):
        self._load_and_compare_data(
            'agg_awc_2017-05-01_4',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-05-01_4.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )

    def test_agg_awc_2017_05_01_5(self):
        self._load_and_compare_data(
            'agg_awc_2017-05-01_5',
            os.path.join(OUTPUT_PATH, 'agg_awc_2017-05-01_5.csv'),
            lambda x: (x['state_id'], x['district_id'], x['block_id'], x['supervisor_id'], x['awc_id'])
        )
        
    def test_agg_child_health_2017_04_01_1(self):
        self._load_and_compare_data(
            'agg_child_health_2017-04-01_1',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-04-01_1.csv')
        )

    def test_agg_child_health_2017_04_01_2(self):
        self._load_and_compare_data(
            'agg_child_health_2017-04-01_2',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-04-01_2.csv')
        )

    def test_agg_child_health_2017_04_01_3(self):
        self._load_and_compare_data(
            'agg_child_health_2017-04-01_3',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-04-01_3.csv')
        )

    def test_agg_child_health_2017_04_01_4(self):
        self._load_and_compare_data(
            'agg_child_health_2017-04-01_4',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-04-01_4.csv')
        )

    def test_agg_child_health_2017_04_01_5(self):
        self._load_and_compare_data(
            'agg_child_health_2017-04-01_5',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-04-01_5.csv')
        )

    def test_agg_child_health_2017_05_01_1(self):
        self._load_and_compare_data(
            'agg_child_health_2017-05-01_1',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-05-01_1.csv')
        )

    def test_agg_child_health_2017_05_01_2(self):
        self._load_and_compare_data(
            'agg_child_health_2017-05-01_2',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-05-01_2.csv')
        )

    def test_agg_child_health_2017_05_01_3(self):
        self._load_and_compare_data(
            'agg_child_health_2017-05-01_3',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-05-01_3.csv')
        )

    def test_agg_child_health_2017_05_01_4(self):
        self._load_and_compare_data(
            'agg_child_health_2017-05-01_4',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-05-01_4.csv')
        )

    def test_agg_child_health_2017_05_01_5(self):
        self._load_and_compare_data(
            'agg_child_health_2017-05-01_5',
            os.path.join(OUTPUT_PATH, 'agg_child_health_2017-05-01_5.csv')
        )
        
    def test_agg_thr_data_2017_04_01_1(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-04-01_1',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-04-01_1.csv')
        )

    def test_agg_thr_data_2017_04_01_2(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-04-01_2',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-04-01_2.csv')
        )

    def test_agg_thr_data_2017_04_01_3(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-04-01_3',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-04-01_3.csv')
        )

    def test_agg_thr_data_2017_04_01_4(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-04-01_4',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-04-01_4.csv')
        )

    def test_agg_thr_data_2017_04_01_5(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-04-01_5',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-04-01_5.csv')
        )

    def test_agg_thr_data_2017_05_01_1(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-05-01_1',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-05-01_1.csv')
        )

    def test_agg_thr_data_2017_05_01_2(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-05-01_2',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-05-01_2.csv')
        )

    def test_agg_thr_data_2017_05_01_3(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-05-01_3',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-05-01_3.csv')
        )

    def test_agg_thr_data_2017_05_01_4(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-05-01_4',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-05-01_4.csv')
        )

    def test_agg_thr_data_2017_05_01_5(self):
        self._load_and_compare_data(
            'agg_thr_data_2017-05-01_5',
            os.path.join(OUTPUT_PATH, 'agg_thr_data_2017-05-01_5.csv')
        )
        
    def test_agg_ccs_record_2017_04_01_1(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-04-01_1',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-04-01_1.csv')
        )

    def test_agg_ccs_record_2017_04_01_2(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-04-01_2',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-04-01_2.csv')
        )

    def test_agg_ccs_record_2017_04_01_3(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-04-01_3',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-04-01_3.csv')
        )

    def test_agg_ccs_record_2017_04_01_4(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-04-01_4',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-04-01_4.csv')
        )

    def test_agg_ccs_record_2017_04_01_5(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-04-01_5',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-04-01_5.csv')
        )

    def test_agg_ccs_record_2017_05_01_1(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-05-01_1',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-05-01_1.csv')
        )

    def test_agg_ccs_record_2017_05_01_2(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-05-01_2',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-05-01_2.csv')
        )

    def test_agg_ccs_record_2017_05_01_3(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-05-01_3',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-05-01_3.csv')
        )

    def test_agg_ccs_record_2017_05_01_4(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-05-01_4',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-05-01_4.csv')
        )

    def test_agg_ccs_record_2017_05_01_5(self):
        self._load_and_compare_data(
            'agg_ccs_record_2017-05-01_5',
            os.path.join(OUTPUT_PATH, 'agg_ccs_record_2017-05-01_5.csv')
        )
