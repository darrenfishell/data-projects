# coding: utf-8

"""
    data.world API

    data.world is designed for data and the people who work with data.  From professional projects to open data, data.world helps you host and share your data, collaborate with your team, and capture context and conclusions as you work.   Using this API users are able to easily access data and manage their data projects regardless of language or tool of preference.  Check out our [documentation](https://dwapi.apidocs.io) for tips on how to get started, tutorials and to interact with the API right within your browser.

    OpenAPI spec version: 0.14.1
    Contact: help@data.world
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class SparqlApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def sparql_get(self, owner, id, query, **kwargs):
        """
        SPARQL query (via GET)
        This endpoint executes SPARQL queries against a dataset or data project.  SPARQL results are available in a variety of formats. By default, `application/sparql-results+json` will be returned. Set the `Accept` header to one of the following values in accordance with your preference:  - `application/sparql-results+xml` - `application/sparql-results+json` - `application/rdf+json` - `application/rdf+xml` - `text/csv` - `text/tab-separated-values`  New to SPARQL? Check out data.world’s[SPARQL tutorial](https://docs.data.world/tutorials/sparql/).
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.sparql_get(owner, id, query, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner: User name and unique identifier of the creator of a dataset or project. For example, in the URL: [https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), jonloyens is the unique identifier of the owner. (required)
        :param str id: Dataset unique identifier. For example, in the URL:[https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), an-intro-to-dataworld-dataset is the unique identifier of the dataset. (required)
        :param str query: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.sparql_get_with_http_info(owner, id, query, **kwargs)
        else:
            (data) = self.sparql_get_with_http_info(owner, id, query, **kwargs)
            return data

    def sparql_get_with_http_info(self, owner, id, query, **kwargs):
        """
        SPARQL query (via GET)
        This endpoint executes SPARQL queries against a dataset or data project.  SPARQL results are available in a variety of formats. By default, `application/sparql-results+json` will be returned. Set the `Accept` header to one of the following values in accordance with your preference:  - `application/sparql-results+xml` - `application/sparql-results+json` - `application/rdf+json` - `application/rdf+xml` - `text/csv` - `text/tab-separated-values`  New to SPARQL? Check out data.world’s[SPARQL tutorial](https://docs.data.world/tutorials/sparql/).
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.sparql_get_with_http_info(owner, id, query, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner: User name and unique identifier of the creator of a dataset or project. For example, in the URL: [https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), jonloyens is the unique identifier of the owner. (required)
        :param str id: Dataset unique identifier. For example, in the URL:[https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), an-intro-to-dataworld-dataset is the unique identifier of the dataset. (required)
        :param str query: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'id', 'query']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method sparql_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `sparql_get`")
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `sparql_get`")
        # verify the required parameter 'query' is set
        if ('query' not in params) or (params['query'] is None):
            raise ValueError("Missing the required parameter `query` when calling `sparql_get`")

        if 'owner' in params and not re.search('[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]', params['owner']):
            raise ValueError("Invalid value for parameter `owner` when calling `sparql_get`, must conform to the pattern `/[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]/`")
        if 'id' in params and not re.search('[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]', params['id']):
            raise ValueError("Invalid value for parameter `id` when calling `sparql_get`, must conform to the pattern `/[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]/`")

        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []
        if 'query' in params:
            query_params.append(('query', params['query']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/sparql-results+json', 'application/sparql-results+xml', 'application/rdf+json', 'application/rdf+xml', 'text/tab-separated-values', 'text/csv'])

        # Authentication setting
        auth_settings = ['token']

        return self.api_client.call_api('/sparql/{owner}/{id}', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def sparql_post(self, owner, id, query, **kwargs):
        """
        SPARQL query
        This endpoint executes SPARQL queries against a dataset or data project.    SPARQL results are available in a variety of formats. By default, `application/sparql-results+json` will be returned. Set the `Accept` header to one of the following values in accordance with your preference:  - `application/sparql-results+xml` - `application/sparql-results+json` - `application/rdf+json` - `application/rdf+xml` - `text/csv` - `text/tab-separated-values`  New to SPARQL? Check out data.world's [SPARQL tutorial](https://docs.data.world/tutorials/sparql/).
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.sparql_post(owner, id, query, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner: User name and unique identifier of the creator of a dataset or project. For example, in the URL: [https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), jonloyens is the unique identifier of the owner. (required)
        :param str id: Dataset unique identifier. For example, in the URL:[https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), an-intro-to-dataworld-dataset is the unique identifier of the dataset. (required)
        :param str query: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.sparql_post_with_http_info(owner, id, query, **kwargs)
        else:
            (data) = self.sparql_post_with_http_info(owner, id, query, **kwargs)
            return data

    def sparql_post_with_http_info(self, owner, id, query, **kwargs):
        """
        SPARQL query
        This endpoint executes SPARQL queries against a dataset or data project.    SPARQL results are available in a variety of formats. By default, `application/sparql-results+json` will be returned. Set the `Accept` header to one of the following values in accordance with your preference:  - `application/sparql-results+xml` - `application/sparql-results+json` - `application/rdf+json` - `application/rdf+xml` - `text/csv` - `text/tab-separated-values`  New to SPARQL? Check out data.world's [SPARQL tutorial](https://docs.data.world/tutorials/sparql/).
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.sparql_post_with_http_info(owner, id, query, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str owner: User name and unique identifier of the creator of a dataset or project. For example, in the URL: [https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), jonloyens is the unique identifier of the owner. (required)
        :param str id: Dataset unique identifier. For example, in the URL:[https://data.world/jonloyens/an-intro-to-dataworld-dataset](https://data.world/jonloyens/an-intro-to-dataworld-dataset), an-intro-to-dataworld-dataset is the unique identifier of the dataset. (required)
        :param str query: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['owner', 'id', 'query']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method sparql_post" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'owner' is set
        if ('owner' not in params) or (params['owner'] is None):
            raise ValueError("Missing the required parameter `owner` when calling `sparql_post`")
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `sparql_post`")
        # verify the required parameter 'query' is set
        if ('query' not in params) or (params['query'] is None):
            raise ValueError("Missing the required parameter `query` when calling `sparql_post`")

        if 'owner' in params and not re.search('[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]', params['owner']):
            raise ValueError("Invalid value for parameter `owner` when calling `sparql_post`, must conform to the pattern `/[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]/`")
        if 'id' in params and not re.search('[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]', params['id']):
            raise ValueError("Invalid value for parameter `id` when calling `sparql_post`, must conform to the pattern `/[a-z0-9](?:-(?!-)|[a-z0-9])+[a-z0-9]/`")

        collection_formats = {}

        path_params = {}
        if 'owner' in params:
            path_params['owner'] = params['owner']
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}
        if 'query' in params:
            form_params.append(('query', params['query']))

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/sparql-results+json', 'application/sparql-results+xml', 'application/rdf+json', 'application/rdf+xml', 'text/tab-separated-values', 'text/csv'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/x-www-form-urlencoded'])

        # Authentication setting
        auth_settings = ['token']

        return self.api_client.call_api('/sparql/{owner}/{id}', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
