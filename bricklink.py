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

class BricklinkApi(object):
    """
    Class represents the Bricklink (https://bricklink.com) API
    """

    """ The Bricklink API end-point """
    BRICKLINK_URL = "https://api.bricklink.com/api/store/v1"

    def _perform_get_request(self, url):
        response = requests.get(url, auth=self._oauth).json()
        if response['meta']['code'] != 200:
            raise BricklinkException(**response['meta'])
        data = response['data']
        return data

    def __init__(self, oauth_consumer_key, oauth_consumer_secret,
                 oauth_access_token, oauth_access_token_secret):
        """
        Creates object which allows commands to the Bricklink API
        :param oauth_consumer_key: The Consumer key provided by Bricklink
        :param oauth_consumer_secret: The Consumer secret provided by Bricklink
        :param oauth_access_token: The Access Token provided by Bricklink
        :param oauth_access_token_secret: The Access Token Secret provided by Bricklink
        """
        self._oauth = OAuth1(
            oauth_consumer_key,
            oauth_consumer_secret,
            oauth_access_token,
            oauth_access_token_secret
        )

    def getCatalogItem(self, type, no):
        """
        Returns information about the specified item in the Bricklink catalog
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :return: If the call is successful it returns a catalog item with the following data structure:
            {
                'item':  {
                    'no': string,
                    'name': string,
                    'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                    'category_id': integer
                },
                'alternate_no': string,
                'image_url': string,
                thumbnail_url': string,
                'weight': fixed point number (2 decimals),
                'dim_x': string (2 decimals),
                'dim_y': string (2 decimals),
                'dim_z': string (2 decimals),
                'year_released': integer,
                'description': string,
                'is_obsolete': boolean,
                'language_code': string
            }
        """
        return self._perform_get_request(
            self.BRICKLINK_URL + "/items/%s/%s" % (type, no))

    def getCatalogItemImage(self, type, no, color_id):
        """
        Returns the image URL of the specified item by color
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: Bricklink color id
        :return: If the call is successful it returns a catalog item with the following data structure
            {
                'color_id': integer,
                'thumbnail_url': string,
                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                'no': string
            }
        """
        return self._perform_get_request(
            self.BRICKLINK_URL + "/items/%s/%s/images/%d" % (type, no, color_id))

    def getCatalogSupersets(self, type, no, color_id = None):
        """
        Returns a list of items that included the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :return: If the call is successful it returns a list of superset entries with the following data structure:
            [
                {
                    'color_id': integer,
                    'entries': [
                        {
                            'quantity': integer,
                            'appears_as': string (A: Alternate, C: Counterpart, E: Extra, R: Regular),
                            'item'  => {
                                'no': string,
                                'name': string,
                                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                                'category_id': integer
                            }
                        },
                        {
                            etc...
                        }
                    ]
                },
                {
                    etc...
                }
            ]
        """
        url = self.BRICKLINK_URL + "/items/%s/%s/supersets" % (type, no)
        if color_id is not None:
            url += "?color_id=%d" % (color_id)

        return self._perform_get_request(url)

    def getCatalogSubsets(self, type, no, color_id = None, box = None, instruction = None,
                          break_minifigs = None, break_subsets = None):
        """
        Returns a list of items that are included in the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :param box: (Optional) Indicates whether the set includes the original box
        :param instruction: (Optional) Indicates whether the set includes the original instruction
        :param break_minifigs: (Optional) Indicates whether the result breaks down minifigs as parts
        :param break_subsets: (Optional) Indicates whether the result breaks down sub sets as parts
        :return: If the call is successful it returns a list of subset entries with the following data structure:
            [
                {
                    'match_no': integer,
                    'entries': [
                        {
                            'color_id': integer,
                            'quantity': integer,
                            'extra_quantity': integer,
                            'is_alternate': boolean,
                            'is_counterpart': boolean,
                            'item': {
                                'no': string,
                                'name': string,
                                'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX),
                                'category_id': integer
                            }
                        },
                        {
                            etc...
                        }
                    ]
                },
                {
                    etc...
                }
            ]
        """
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

        return self._perform_get_request(url)

    def getCatalogPriceGuide(self, type, no, color_id = None, guide_type = None, new_or_used = None,
                             country_code = None, region = None, currency_code = None, vat = None):
        """
        Returns the price statistics of the specified item
        :param type: The type of item. Acceptable values are:
                        MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
        :param no: Identification number of the item
        :param color_id: (Optional) Bricklink color id
        :param guide_type: (Optional) Indicates which statistics should be provided. Acceptable values are:
                            "sold": get the price statistics of "Last 6 months sales"
                            "stock": get the price statistics of "Current items for sale" (default)
        :param new_or_used: (Optional) Indicates the condition of the items that are included in the statistics.
                            Acceptable values are:
                                "N": new item (default), "U": used item
        :param country_code: (Optional) The result includes only items in stores which are located in the specified country
        :param region: (Optional) The result includes only items in stores which are located in the specified region
        :param currency_code: (Optional) The currency in which prices should be returned
        :param vat: (Optional) Indicates that price will include VAT for items from VAT enabled stores.
                    Acceptable values are: "N": exclude VAT (default), "Y": include VAT
        :return: If the call is successful it returns a price guide resource with the following data structure:
            {
                'item': {
                    'no': string,
                    'type': string (MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX)
                },
                'new_or_used': string (N: New, U: Used)
                'currency_code': string,
                'min_price': fixed point number (4 decimals),
                'max_price': fixed point number (4 decimals),
                'avg_price': fixed point number (4 decimals),
                'qty_avg_price': fixed_point_number (4 decimals),
                'unit_quantity': integer,
                'total_quantity': integer,
                'price_detail': [
                    {
                        'quantity': integer,
                        'unit_price': fixed point number (4 decimals),
                        'shipping_available': string
                            __OR__
                        'quantity': integer,
                        'unit_price': integer,
                        'seller_country_code': string,
                        'buyer_country_code': string,
                        'date_ordered': timestamp
                    },
                    {
                        etc...
                    }
                ]
            }
        """
        url = self.BRICKLINK_URL + "/items/%s/%s/price" % (type, no)

        optional_params = []
        if color_id:
            optional_params.append("color_id=%d" % color_id)
        if guide_type:
            optional_params.append("guide_type=%s" % guide_type)
        if new_or_used:
            optional_params.append("new_or_used=%s" % new_or_used)
        if country_code:
            optional_params.append("country_code=%s" % country_code)
        if region:
            optional_params.append("region=%s" % region)
        if currency_code:
            optional_params.append("currency_code=%s" % currency_code)
        if vat:
            optional_params.append("vat=%s" % vat)

        url += "?%s" % ("&".join(optional_params))

        return self._perform_get_request(url)
