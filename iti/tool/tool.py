import base64
import hashlib
import hmac
from datetime import datetime
from email.utils import formatdate
from time import mktime


class Tool:

    @classmethod
    def get_header_date(cls):
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return formatdate(timeval=stamp, localtime=False, usegmt=True)

    @classmethod
    def format_authorization(cls, access_key, signature):
        return 'KSTI %s:%s' % (access_key, signature)

    @classmethod
    def get_canonicalized_resource(cls, pathname, query):
        if len(query) <= 0:
            return pathname

        resource = '%s?' % pathname
        for key in sorted(query):
            if query[key] is not None:
                s = '%s=%s&' % (key, query[key])
                resource += s
        return resource[:-1]

    @classmethod
    def get_canonicalized_headers(cls, headers):
        canon_keys = list(filter(lambda k: k.startswith('x-api'), headers))
        canon_header_list = ['%s:%s\n' % (i, headers[i]) for i in sorted(canon_keys)]
        canon_header = ''.join(canon_header_list)
        return canon_header

    @classmethod
    def get_signature(cls, string_to_sign, secret):
        hash_val = hmac.new(
            secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(hash_val).decode('utf-8')
        return signature

    @classmethod
    def get_string_to_sign(cls, method, pathname, headers, query):
        content_md5 = '' if headers.get('content-md5') is None else headers.get('content-md5')
        content_type = '' if headers.get('content-type') is None else headers.get('content-type')
        accept = '' if headers.get('accept') is None else headers.get('accept')
        date = '' if headers.get('date') is None else headers.get('date')

        header = '%s\n%s\n%s\n%s\n%s\n' % (method, accept, content_md5, content_type, date)
        canon_headers = cls.get_canonicalized_headers(headers)
        canon_resource = cls.get_canonicalized_resource(pathname, query)
        sign_str = header + canon_headers + canon_resource
        return sign_str
