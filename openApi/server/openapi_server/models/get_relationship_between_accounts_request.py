# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.get_relationship_between_accounts_request_params import GetRelationshipBetweenAccountsRequestParams
from openapi_server import util

from openapi_server.models.get_relationship_between_accounts_request_params import GetRelationshipBetweenAccountsRequestParams  # noqa: E501

class GetRelationshipBetweenAccountsRequest(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, jsonrpc='2.0', method=None, params=None, id=1):  # noqa: E501
        """GetRelationshipBetweenAccountsRequest - a model defined in OpenAPI

        :param jsonrpc: The jsonrpc of this GetRelationshipBetweenAccountsRequest.  # noqa: E501
        :type jsonrpc: str
        :param method: The method of this GetRelationshipBetweenAccountsRequest.  # noqa: E501
        :type method: str
        :param params: The params of this GetRelationshipBetweenAccountsRequest.  # noqa: E501
        :type params: GetRelationshipBetweenAccountsRequestParams
        :param id: The id of this GetRelationshipBetweenAccountsRequest.  # noqa: E501
        :type id: int
        """
        self.openapi_types = {
            'jsonrpc': str,
            'method': str,
            'params': GetRelationshipBetweenAccountsRequestParams,
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
    def from_dict(cls, dikt) -> 'GetRelationshipBetweenAccountsRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GetRelationshipBetweenAccountsRequest of this GetRelationshipBetweenAccountsRequest.  # noqa: E501
        :rtype: GetRelationshipBetweenAccountsRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def jsonrpc(self):
        """Gets the jsonrpc of this GetRelationshipBetweenAccountsRequest.


        :return: The jsonrpc of this GetRelationshipBetweenAccountsRequest.
        :rtype: str
        """
        return self._jsonrpc

    @jsonrpc.setter
    def jsonrpc(self, jsonrpc):
        """Sets the jsonrpc of this GetRelationshipBetweenAccountsRequest.


        :param jsonrpc: The jsonrpc of this GetRelationshipBetweenAccountsRequest.
        :type jsonrpc: str
        """
        if jsonrpc is None:
            raise ValueError("Invalid value for `jsonrpc`, must not be `None`")  # noqa: E501

        self._jsonrpc = jsonrpc

    @property
    def method(self):
        """Gets the method of this GetRelationshipBetweenAccountsRequest.


        :return: The method of this GetRelationshipBetweenAccountsRequest.
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """Sets the method of this GetRelationshipBetweenAccountsRequest.


        :param method: The method of this GetRelationshipBetweenAccountsRequest.
        :type method: str
        """
        allowed_values = ["bridge.get_relationship_between_accounts"]  # noqa: E501
        if method not in allowed_values:
            raise ValueError(
                "Invalid value for `method` ({0}), must be one of {1}"
                .format(method, allowed_values)
            )

        self._method = method

    @property
    def params(self):
        """Gets the params of this GetRelationshipBetweenAccountsRequest.


        :return: The params of this GetRelationshipBetweenAccountsRequest.
        :rtype: GetRelationshipBetweenAccountsRequestParams
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this GetRelationshipBetweenAccountsRequest.


        :param params: The params of this GetRelationshipBetweenAccountsRequest.
        :type params: GetRelationshipBetweenAccountsRequestParams
        """
        if params is None:
            raise ValueError("Invalid value for `params`, must not be `None`")  # noqa: E501

        self._params = params

    @property
    def id(self):
        """Gets the id of this GetRelationshipBetweenAccountsRequest.


        :return: The id of this GetRelationshipBetweenAccountsRequest.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this GetRelationshipBetweenAccountsRequest.


        :param id: The id of this GetRelationshipBetweenAccountsRequest.
        :type id: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id