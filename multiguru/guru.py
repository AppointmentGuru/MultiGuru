from django.conf import settings

def get_headers(user_id, consumer=settings.SERVICE_NAME):
    return {
        'X_ANONYMOUS_CONSUMER': 'False',
        'X_AUTHENTICATED_USERID': str(user_id),
        'X_CONSUMER_USERNAME': consumer,
    }