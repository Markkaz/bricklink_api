import requests
from requests_oauthlib import OAuth1

class BricklinkException(Exception):
    def __init__(self, code, message, description):
        self.code = code
        self.message = message
        self.description = description
        super(BricklinkException, self).__init__(self)

    def __str__(self):
        return "%d - %s: %s" % (self.code, self.message, self.description)

class CatelogItem(object):
    def __init__(self, no, name, type, category_id, image_url, thumbnail_url, weight, dim_x, dim_y, dim_z,
                 year_released, is_obsolete, alternate_no = None, description = None, language_code = None):
        self.no = no
        self.name = name
        self.type = type
        self.catelog_id = category_id
        self.alternate_no = alternate_no
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.weight = weight
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.dim_z = dim_z
        self.year_released = year_released
        self.description = description
        self.is_obsolete = is_obsolete
        self.language_code = language_code

    def __str__(self):
        return "%s %s - %s" % (self.type, self.no, self.name)

class BricklinkApi(object):
    BRICKLINK_URL = "https://api.bricklink.com/api/store/v1"

    def __init__(self, oauth_consumer_key, oauth_consumer_secret,
                 oauth_access_token, oauth_access_token_secret):
        self._oauth = OAuth1(
            oauth_consumer_key,
            oauth_consumer_secret,
            oauth_access_token,
            oauth_access_token_secret
        )

    def getCatelogItem(self, type, no):
        url = self.BRICKLINK_URL + "/items/%s/%s" % (type, no)
        response = requests.get(url, auth=self._oauth).json()

        if response['meta']['code'] != 200:
            raise BricklinkException(**response['meta'])

        return CatelogItem(**response['data'])