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
    def __init__(self, no, type, color_id = None, name = None, category_id = None, image_url = None, thumbnail_url = None,
                 weight = None, dim_x = None, dim_y = None, dim_z = None, year_released = None,
                 is_obsolete = False, alternate_no = None, description = None, language_code = None):
        self.no = no
        self.name = name
        self.type = type
        self.color_id = color_id
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

class CatelogSuperSet(object):
    def __init__(self, quantity, appears_as, item, color_id):
        self.quantity = quantity,
        self.appears_as = appears_as
        self.item = CatelogItem(color_id = color_id, **item)

    def __str__(self):
        return "%s %s %s" % (str(self.quantity), self.appears_as, self.item)

class CatelogSuperSetEntries(object):
    def __init__(self, entries):
        self._entries = entries['entries']
        self._color_id = entries['color_id']

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, key):
        return CatelogSuperSet(color_id = self._color_id, **self._entries[key])

class CatelogSupersetEntriesList(object):
    def __init__(self, items):
        self._items = items

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        return CatelogSuperSetEntries(self._items[key])

class CatelogSubsetEntries(object):
    def __init__(self, entries):
        self._entries = []
        for entry in entries:
            self._entries += entry['entries']

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, key):
        return CatelogSubsetEntry(**self._entries[key])

    def __str__(self):
        return str(self._entries)

class CatelogSubsetEntry(object):
    def __init__(self, item, color_id, quantity, extra_quantity, is_alternate, is_counterpart):
        self.quantity = quantity
        self.extra_quantity = extra_quantity
        self.is_alternate = is_alternate
        self.color_id = color_id
        self.is_counterpart = is_counterpart
        self.item = CatelogItem(**item)

    def __str__(self):
        return "%s and extra %s of %s in color %s" % (self.quantity, self.extra_quantity, self.item, self.color_id)

class BricklinkApi(object):
    BRICKLINK_URL = "https://api.bricklink.com/api/store/v1"

    def _perform_get_request(self, url):
        response = requests.get(url, auth=self._oauth).json()
        if response['meta']['code'] != 200:
            raise BricklinkException(**response['meta'])
        data = response['data']
        return data

    def __init__(self, oauth_consumer_key, oauth_consumer_secret,
                 oauth_access_token, oauth_access_token_secret):
        self._oauth = OAuth1(
            oauth_consumer_key,
            oauth_consumer_secret,
            oauth_access_token,
            oauth_access_token_secret
        )

    def getCatelogItem(self, type, no):
        data = self._perform_get_request(
            self.BRICKLINK_URL + "/items/%s/%s" % (type, no))
        return CatelogItem(**data)

    def getCatelogItemImage(self, type, no, color_id):
        data = self._perform_get_request(
            self.BRICKLINK_URL + "/items/%s/%s/images/%d" % (type, no, color_id))
        return CatelogItem(**data)

    def getCatelogSupersets(self, type, no, color_id = None):
        url = self.BRICKLINK_URL + "/items/%s/%s/supersets" % (type, no)
        if color_id is not None:
            url += "?color_id=%d" % (color_id)

        return CatelogSupersetEntriesList(self._perform_get_request(url))

    def getCatelogSubsets(self, type, no, color_id = None, box = None, instruction = None,
                          break_minifigs = None, break_subsets = None):
        url = self.BRICKLINK_URL + "/items/%s/%s/subsets" % (type, no)

        optional_params = []
        if color_id:
            optional_params.append("color_id=%d" % color_id)
        if box:
            optional_params.append("box=%r" % box)
        if instruction:
            optional_params.append("instruction=%r" % instruction)
        if break_minifigs:
            optional_params.append("break_minifigs=%r" % break_minifigs)
        if break_subsets:
            optional_params.append("break_subsets=%r" % break_subsets)

        url += "?%s" % ("&".join(optional_params))

        return CatelogSubsetEntries(self._perform_get_request(url))
