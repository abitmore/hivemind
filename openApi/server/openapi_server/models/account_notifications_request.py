# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.account_notifications_request_params import AccountNotificationsRequestParams
from openapi_server import util

from openapi_server.models.account_notifications_request_params import AccountNotificationsRequestParams  # noqa: E501

class AccountNotificationsRequest(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, jsonrpc='2.0', method=None, params=None, id=1):  # noqa: E501
        """AccountNotificationsRequest - a model defined in OpenAPI

        :param jsonrpc: The jsonrpc of this AccountNotificationsRequest.  # noqa: E501
        :type jsonrpc: str
        :param method: The method of this AccountNotificationsRequest.  # noqa: E501
        :type method: str
        :param params: The params of this AccountNotificationsRequest.  # noqa: E501
        :type params: AccountNotificationsRequestParams
        :param id: The id of this AccountNotificationsRequest.  # noqa: E501
        :type id: int
        """
        self.openapi_types = {
            'jsonrpc': str,
            'method': str,
            'params': AccountNotificationsRequestParams,
            'id': int
        }

        self.attribute_map = {
            'jsonrpc': 'jsonrpc',
            'method': 'method',
            'params': 'params',
            'id': 'id'
        }

        self._jsonrpc = jsonrpc
        self._method = method
        self._params = params
        self._id = id

    @classmethod
    def from_dict(cls, dikt) -> 'AccountNotificationsRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AccountNotificationsRequest of this AccountNotificationsRequest.  # noqa: E501
        :rtype: AccountNotificationsRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def jsonrpc(self):
        """Gets the jsonrpc of this AccountNotificationsRequest.


        :return: The jsonrpc of this AccountNotificationsRequest.
        :rtype: str
        """
        return self._jsonrpc

    @jsonrpc.setter
    def jsonrpc(self, jsonrpc):
        """Sets the jsonrpc of this AccountNotificationsRequest.


        :param jsonrpc: The jsonrpc of this AccountNotificationsRequest.
        :type jsonrpc: str
        """
        if jsonrpc is None:
            raise ValueError("Invalid value for `jsonrpc`, must not be `None`")  # noqa: E501

        self._jsonrpc = jsonrpc

    @property
    def method(self):
        """Gets the method of this AccountNotificationsRequest.


        :return: The method of this AccountNotificationsRequest.
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """Sets the method of this AccountNotificationsRequest.


        :param method: The method of this AccountNotificationsRequest.
        :type method: str
        """
        allowed_values = ["bridge.account_notifications"]  # noqa: E501
        if method not in allowed_values:
            raise ValueError(
                "Invalid value for `method` ({0}), must be one of {1}"
                .format(method, allowed_values)
            )

        self._method = method

    @property
    def params(self):
        """Gets the params of this AccountNotificationsRequest.


        :return: The params of this AccountNotificationsRequest.
        :rtype: AccountNotificationsRequestParams
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this AccountNotificationsRequest.


        :param params: The params of this AccountNotificationsRequest.
        :type params: AccountNotificationsRequestParams
        """
        if params is None:
            raise ValueError("Invalid value for `params`, must not be `None`")  # noqa: E501

        self._params = params

    @property
    def id(self):
        """Gets the id of this AccountNotificationsRequest.


        :return: The id of this AccountNotificationsRequest.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AccountNotificationsRequest.


        :param id: The id of this AccountNotificationsRequest.
        :type id: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id