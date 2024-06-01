# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.TokenAuthentication',
#     ),
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#     'PAGE_SIZE': 10,
#
#     'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
# }
REST_FRAMEWORK = {

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend',
                                ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}