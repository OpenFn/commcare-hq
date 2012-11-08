from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.reminders.views',
    url(r'^$', 'default', name='reminders_default'),
    url(r'^all/$', 'list_reminders', name='list_reminders'),
    url(r'^add_fixed/$', 'add_reminder', name='add_reminder'),
    url(r'^edit_fixed/(?P<handler_id>[\w-]+)/$', 'add_reminder', name='edit_reminder'),
    url(r'^delete/(?P<handler_id>[\w-]+)/$', 'delete_reminder', name='delete_reminder'),
    url(r'^scheduled/', 'scheduled_reminders', name='scheduled_reminders'),
    url(r'^add_complex/', 'add_complex_reminder_schedule', name='add_complex_reminder_schedule'),
    url(r'^edit_complex/(?P<handler_id>[\w-]+)/$', 'add_complex_reminder_schedule', name='edit_complex'),
    url(r'^manage_keywords/$', 'manage_keywords', name='manage_keywords'),
    url(r'^add_keyword/$', 'add_keyword', name='add_keyword'),
    url(r'^edit_keyword/(?P<keyword_id>[\w-]+)/$', 'add_keyword', name='edit_keyword'),
    url(r'^delete_keyword/(?P<keyword_id>[\w-]+)/$', 'delete_keyword', name='delete_keyword'),
    url(r'^survey_list/$', 'survey_list', name='survey_list'),
    url(r'^add_survey/$', 'add_survey', name='add_survey'),
    url(r'^edit_survey/(?P<survey_id>[\w-]+)/$', 'add_survey', name='edit_survey'),
    url(r'^add_sample/$', 'add_sample', name='add_sample'),
    url(r'^edit_sample/(?P<sample_id>[\w-]+)/$', 'add_sample', name='edit_sample'),
    url(r'^sample_list/$', 'sample_list', name='sample_list'),
)
