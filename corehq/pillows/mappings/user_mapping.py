USER_INDEX="hqusers_55adf53b5021867f35c6649ad589e493"
USER_MAPPING={'_all': {'analyzer': 'standard'},
 '_meta': {'comment': ' [yedi made on 11/13/2013',
           'created': None},
 'date_detection': False,
 'date_formats': ['yyyy-MM-dd',
                  "yyyy-MM-dd'T'HH:mm:ssZZ",
                  "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
                  "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'",
                  "yyyy-MM-dd'T'HH:mm:ss'Z'",
                  "yyyy-MM-dd'T'HH:mm:ssZ",
                  "yyyy-MM-dd'T'HH:mm:ssZZ'Z'",
                  "yyyy-MM-dd'T'HH:mm:ss.SSSZZ",
                  "yyyy-MM-dd'T'HH:mm:ss",
                  "yyyy-MM-dd' 'HH:mm:ss",
                  "yyyy-MM-dd' 'HH:mm:ss.SSSSSS",
                  "mm/dd/yy' 'HH:mm:ss"],
 'dynamic': False,
 'properties': {'CURRENT_VERSION': {'type': 'string'},
                'base_doc': {'type': 'string'},
                'created_on': {'format': "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ssZZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ssZZ'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSZZ||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss.SSSSSS||mm/dd/yy' 'HH:mm:ss",
                               'type': 'date'},
                'date_joined': {'format': "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ssZZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ssZZ'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSZZ||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss.SSSSSS||mm/dd/yy' 'HH:mm:ss",
                                'type': 'date'},
                'doc_type': {'index': 'not_analyzed', 'type': 'string'},
                'domain': {'fields': {'domain': {'index': 'analyzed',
                                                 'type': 'string'},
                                      'exact': {'index': 'not_analyzed',
                                                'type': 'string'}},
                           'type': 'multi_field'},
                'domain_membership': {'dynamic': False,
                                      'properties': {'doc_type': {'index': 'not_analyzed',
                                                                  'type': 'string'},
                                                     'domain': {'fields': {'domain': {'index': 'analyzed',
                                                                                      'type': 'string'},
                                                                           'exact': {'index': 'not_analyzed',
                                                                                     'type': 'string'}},
                                                                'type': 'multi_field'},
                                                     'is_admin': {'type': 'boolean'},
                                                     'override_global_tz': {'type': 'boolean'},
                                                     'role_id': {'type': 'string'},
                                                     'timezone': {'type': 'string'}},
                                      'type': 'object'},
                'email_opt_out': {'type': 'boolean'},
                'eulas': {'dynamic': False,
                          'properties': {'date': {'format': "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ssZZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ssZZ'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSZZ||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss.SSSSSS||mm/dd/yy' 'HH:mm:ss",
                                                  'type': 'date'},
                                         'doc_type': {'index': 'not_analyzed',
                                                      'type': 'string'},
                                         'signed': {'type': 'boolean'},
                                         'type': {'type': 'string'},
                                         'user_id': {'type': 'string'},
                                         'user_ip': {'type': 'string'},
                                         'version': {'type': 'string'}},
                          'type': 'object'},
                'first_name': {'type': 'string'},
                'is_active': {'type': 'boolean'},
                'is_staff': {'type': 'boolean'},
                'is_superuser': {'type': 'boolean'},
                'language': {'type': 'string'},
                'last_login': {'format': "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ssZZ||yyyy-MM-dd'T'HH:mm:ss.SSSSSS||yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd'T'HH:mm:ssZ||yyyy-MM-dd'T'HH:mm:ssZZ'Z'||yyyy-MM-dd'T'HH:mm:ss.SSSZZ||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss||yyyy-MM-dd' 'HH:mm:ss.SSSSSS||mm/dd/yy' 'HH:mm:ss",
                               'type': 'date'},
                'last_name': {'type': 'string'},
                'password': {'type': 'string'},
                'registering_device_id': {'type': 'string'},
                'status': {'type': 'string'},
                'user_data': {'dynamic': True, 'type': 'object'},
                'username': {'fields': {'exact': {'include_in_all': False,
                                                  'index': 'not_analyzed',
                                                  'type': 'string'},
                                        'username': {'analyzer': 'standard',
                                                     'index': 'analyzed',
                                                     'type': 'string'}},
                             'type': 'multi_field'}}}