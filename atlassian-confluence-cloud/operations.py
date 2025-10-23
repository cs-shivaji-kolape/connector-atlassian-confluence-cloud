"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

import json
import requests
import time
from connectors.core.connector import get_logger, ConnectorError
from requests.auth import HTTPBasicAuth
from datetime import datetime

logger = get_logger('atlassian-confluence-cloud')


class AtlassianConfluenceCloud(object):
    def __init__(self, config):
        self.server_url = config.get('server_url', '').strip('/')
        if not self.server_url.startswith('https://') and not self.server_url.startswith('http://'):
            self.server_url = ('https://{0}'.format(self.server_url))
        self.username = config.get('username')
        self.api_token = config.get('api_token')
        self.verify_ssl = config.get('verify_ssl')
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def make_rest_call(self, endpoint, params=None, payload=None, method='GET'):
        auth = HTTPBasicAuth(self.username, self.api_token)
        service_endpoint = '{0}{1}'.format(self.server_url, endpoint)
        logger.debug('REST API Request Endpoint: {0}'.format(service_endpoint))
        logger.debug('REST API Request Payload: {0}'.format(payload))
        logger.debug('REST API Request Params: {0}'.format(params))
        try:
            response = requests.request(method, service_endpoint, auth=auth, params=params, data=payload,
                                        verify=self.verify_ssl, headers=self.headers)
            logger.debug('REST API Response Status Code: {0}'.format(response.status_code))
            if response.ok:
                if response.text:
                    return response.json()
            else:
                if response.text != "":
                    err_resp = response.json()
                    raise ConnectorError(str(err_resp))
                else:
                    error_msg = '{0}: {1}'.format(response.status_code, response.reason)
                    raise ConnectorError(error_msg)
        except requests.exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except requests.exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except requests.exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except requests.exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as e:
            logger.error('{0}'.format(e))
            raise ConnectorError('{0}'.format(e))


def build_params(params):
    return {k: v for k, v in params.items() if v is not None and v != ''}


def get_str_to_list(input_str):
    if isinstance(input_str, str):
        input_str = input_str if isinstance(input_str, int) else input_str.split(',')
    if isinstance(input_str, list):
        input_str = [str(x).strip() for x in input_str]
    return input_str


def get_epoch_time(value):
    try:
        dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        epoch_seconds = dt.timestamp()
        epoch_millis = int(epoch_seconds * 1000)
        return epoch_millis
    except Exception as e:
        logger.error(f"Error converting date time in epoch format: {e}")
        return value


def create_space(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    representation = params.pop('representation', '')
    value = params.pop('value', '')
    if representation and value:
        params.update({'description': {"representation": representation, "value": value}})
    payload = json.dumps(params)
    return client.make_rest_call('/wiki/api/v2/spaces', payload=payload, method='POST')


def get_spaces(config, params):
    client = AtlassianConfluenceCloud(config)
    params['type'] = params.get('type', '').replace(' ', '_').lower()
    params['status'] = params.get('status', '').lower()
    params['description-format'] = params.get('description-format', '').lower()
    params = build_params(params)
    spaces_ids = params.pop('ids', '')
    if spaces_ids:
        spaces_ids = get_str_to_list(spaces_ids)
        params.update({'ids': spaces_ids})
    spaces_keys = params.pop('keys', '')
    if spaces_keys:
        spaces_keys = get_str_to_list(spaces_keys)
        params.update({'keys': spaces_keys})
    labels = params.pop('labels', '')
    if labels:
        labels = get_str_to_list(labels)
        params.update({'labels': labels})
    return client.make_rest_call('/wiki/api/v2/spaces', params=params)


def get_specific_space_details(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    space_id = params.pop('id', '')
    endpoint = f'/wiki/api/v2/spaces/{space_id}'
    return client.make_rest_call(endpoint, params=params)


def create_custom_content(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    representation = params.pop('representation', '').lower()
    value = params.pop('value', '')
    if representation and value:
        params.update({'body': {"representation": representation, "value": value}})
    payload = json.dumps(params)
    return client.make_rest_call('/wiki/api/v2/custom-content', payload=payload, method='POST')


def get_specific_custom_content(config, params):
    client = AtlassianConfluenceCloud(config)
    params['body-format'] = params.get('body-format', '').replace(' ', '_').lower()
    params = build_params(params)
    custom_content_id = params.pop('id', '')
    endpoint = f'/wiki/api/v2/custom-content/{custom_content_id}'
    return client.make_rest_call(endpoint, params=params)


def get_custom_contents(config, params):
    client = AtlassianConfluenceCloud(config)
    params['body-format'] = params.get('body-format', '').replace(' ', '_').lower()
    params = build_params(params)
    custom_content_id = params.pop('ids', '')
    if custom_content_id:
        custom_content_id = get_str_to_list(custom_content_id)
        params.update({'ids': custom_content_id})
    space_id = params.pop('space-id', '')
    if custom_content_id:
        space_id = get_str_to_list(space_id)
        params.update({'space-id': space_id})
    return client.make_rest_call('/wiki/api/v2/custom-content', params=params)


def update_custom_content(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    custom_content_id = params.get('id')
    params['status'] = params.get('status', '').lower()
    representation = params.pop('representation', '')
    value = params.pop('value', '')
    if representation and value:
        params.update({'body': {"representation": representation, "value": value}})
    version_number = params.pop('number', '')
    version_message = params.pop('message', '')
    if version_number and version_message:
        params.update({'version': {"number": version_number, "message": version_message}})
    endpoint = f'/wiki/api/v2/custom-content/{custom_content_id}'
    payload = json.dumps(params)
    return client.make_rest_call(endpoint, payload=json.dumps(payload), method='PUT')


def delete_custom_content(config, params):
    client = AtlassianConfluenceCloud(config)
    content_id = params.pop('id', '')
    params = build_params(params)
    endpoint = f'/wiki/api/v2/custom-content/{content_id}'
    resp = client.make_rest_call(endpoint, method='DELETE', params=params)
    return {"status": "success", "message": "Custom Content successfully deleted",
            "content_id": content_id} if not resp else resp


def create_footer_comment(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    representation = params.pop('representation', '')
    value = params.pop('value', '')
    if representation and value:
        params.update({'body': {"representation": representation, "value": value}})
    return client.make_rest_call('/wiki/api/v2/footer-comments', params=params, method='POST')


def get_groups(config, params):
    client = AtlassianConfluenceCloud(config)
    params['accessType'] = params.get('accessType', '').replace(' ', '-').lower()
    params = build_params(params)
    return client.make_rest_call('/wiki/rest/api/group', params=params)


def get_users(config, params):
    client = AtlassianConfluenceCloud(config)
    account_ids = params.pop('accountId', [])
    params['accountId'] = get_str_to_list(account_ids)
    params = build_params(params)
    return client.make_rest_call('/wiki/rest/api/user/bulk', params=params)


def get_audit_records(config, params):
    client = AtlassianConfluenceCloud(config)
    params = build_params(params)
    start_date = params.get('startDate')
    if start_date:
        start_date = get_epoch_time(start_date)
        params['startDate'] = start_date
    end_date = params.get('endDate')
    if end_date:
        end_date = get_epoch_time(end_date)
        params['endDate'] = end_date
    return client.make_rest_call('/wiki/rest/api/audit', params=params)


def get_attachments(config, params):
    client = AtlassianConfluenceCloud(config)
    params['status'] = params.get('status', '').strip(',')
    params = build_params(params)
    return client.make_rest_call('/wiki/api/v2/attachments', params=params)


def _check_health(config):
    try:
        params = {}
        return get_attachments(config, params)
    except Exception as e:
        logger.error(e)
        raise ConnectorError('{0}'.format(e))


operations = {
    'create_space': create_space,
    'get_spaces': get_spaces,
    'get_specific_space_details': get_specific_space_details,
    'create_custom_content': create_custom_content,
    'get_specific_custom_content': get_specific_custom_content,
    'get_custom_contents': get_custom_contents,
    'update_custom_content': update_custom_content,
    'delete_custom_content': delete_custom_content,
    'create_footer_comment': create_footer_comment,
    'get_groups': get_groups,
    'get_users': get_users,
    'get_audit_records': get_audit_records,
    'get_attachments': get_attachments
}
