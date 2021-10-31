from itsdangerous import URLSafeTimedSerializer
from django.core.mail import send_mail
from django.db.models import Q

# from movies.settings import SECRET_KEY, SECURITY_PASSWORD_SALT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from movies import settings
from movies.settings import SECRET_KEY, SECURITY_PASSWORD_SALT


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)


# def trigger_email(**kwargs):
#     subject = kwargs.get('subject', 'Email From IMDB')
#     message = kwargs.get('message', 'Message from IMDB')
#     receipients = kwargs.get('to', [])
#     from_email = kwargs.get("sender", EMAIL_HOST_USER)
#     password = kwargs.get('password', EMAIL_HOST_PASSWORD)
#     send_mail(**{"subject":subject,
#                  "message":message,
#                  "from_email":from_email,
#                  "recipient_list":receipients,
#                  'auth_user':from_email,
#                  'auth_password':password
#                  })


def confirm_token(token, expiration=604800):
    """

    :param token: Token info
    :param expiration: Expiration time in seconds
    :return:
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        return False
    return email


def build_search_filter(request, model):
    """
    To build search query and query on the model provided
    :param request:
    :param model:
    :return:
    """

    q_objects = Q()
    fields = model.SEARCH_FIELDS
    query = request.query_params.dict()
    for field in fields:
       q_objects |= Q(**{"{}__icontains".format(field):query['search']})

    return model.objects.filter(q_objects)

def request_sort_to_sort_dict(request_fields, serializer, sorts=[]):
    """
    convert the requeted sort fields to sort fields dictionary
    extract the sort fields from request dict
    filter the field which has prefix as defined request_sort_field_prefix
    validate the extracted values with serializer
    raise validation error when invalid serializer fails
    """
    sort_prefix = "sort_"
    sorter = lambda field, direction: "-%s" % field if direction < 1 else field
    sort_fields = {
        key[len(sort_prefix)::]:int(request_fields.get(key)) for key in request_fields.keys() if key.startswith(sort_prefix)
    }

    return [sorter(key, value) for key, value in sort_fields.items()] + sorts


