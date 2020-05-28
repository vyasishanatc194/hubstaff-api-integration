# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

from hubstaff.exceptions import *


class HubstaffClient:
    api_url = 'https://api.hubstaff.com/v1'
    auth_endpoint = '/auth'
    organizations_list_endpoint = '/organizations'
    custom_by_date_team_endpoint = '/custom/by_date/team'

    def __init__(self, app_token, auth_token=None,
                 username=None, password=None):
        self._app_token = app_token
        if not auth_token and not(username and password):
            raise ValueError('auth_token or (username, password) '
                             'pair must be set')
        self._auth_token = auth_token
        self._username = username
        self._password = password

    def authenticate(self):
        if not self._username or not self._password:
            return self._auth_token

        resp = requests.post(
            '%s%s' % (self.api_url, self.auth_endpoint),
            headers={'App-Token': self._app_token},
            data={'email': self._username, 'password': self._password})

        if resp.status_code == 200:
            self._auth_token = resp.json()['user']['auth_token']
        elif resp.status_code == 401:
            raise HubstaffAuthError(resp.json()['error'])
        else:
            raise HubstaffError(resp.json()['error'])

        return self._auth_token

    def _request(self, method, endpoint, params=None, headers=None,
                 data=None, json=None, refresh_token=False):
        """Make rest api request.

        :param str method: rest api method
        :param str endpoint: rest api endpoint
        :param dict params: (optional) query params
        :param dict headers: (optional) additional headers
        :param dict data: (optional) form data content
        :param dict or list json: (optional) json data content
        :param bool refresh_token: auth_token refreshes if True
        :return dict or list: json response data
        """
        if not self._auth_token or refresh_token:
            self.authenticate()

        headers = headers.copy() if headers else {}
        headers.update({'App-Token': self._app_token,
                        'Auth-Token': self._auth_token})

        resp = requests.request(
            method, '%s%s' % (self.api_url, endpoint),
            params=params, headers=headers, data=data, json=json)

        if resp.status_code == 401:
            if not refresh_token:
                # token can be expired, needs to refresh
                return self._request(method, endpoint,
                                     params=params,
                                     headers=headers,
                                     data=data,
                                     json=json,
                                     refresh_token=True)
            # token was refreshed, but 401 response still happens
            raise HubstaffAuthError(resp.json()['error'])

        result = resp.json()
        if 'error' in result:
            raise HubstaffError(result['error'])

        return result

    def _get(self, endpoint, params=None, **kwargs):
        return self._request('get', endpoint, params=params, **kwargs)
    
    def get_organizations_list(self, offset=0):
        result = self._get(self.organizations_list_endpoint,
                           params={'offset': offset})
        organizations_list = result['organizations']
        return organizations_list

    def get_custom_by_date_team_endpoint(self, start_date,
                                            end_date,
                                            organization_id_list=None,
                                            user_id_list=None,
                                            project_id_list=None):
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }

        if user_id_list:
            params['users'] = ','.join(map(str, user_id_list))

        if organization_id_list:
            params['organizations'] = ','.join(map(str, organization_id_list))

        if project_id_list:
            params['projects'] = ','.join(map(str, project_id_list))
        result = self._get(self.custom_by_date_team_endpoint, params=params)
        custom_by_date_team_list = result['organizations']
        return custom_by_date_team_list
