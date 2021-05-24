import demistomock as demisto
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import
from CommonServerUserPython import *  # noqa

import requests
import copy

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

''' CONSTANTS '''

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # ISO8601 format with UTC, default in XSOAR

''' CLIENT CLASS '''


@logger
class Client(BaseClient):
    """
    Client class to interact with the service API
    This Client implements API calls, and does not contain any XSOAR logic.
    Should only do requests and return data.
    """

    def __init__(self, base_url, verify, api_token, proxy):
        headers = {'X-Arbux-APIToken': api_token}
        super().__init__(base_url=base_url, verify=verify, headers=headers, proxy=proxy)

    # countries
    def country_code_list_command(self, args: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/countries/', params=args)

    def outbound_blacklisted_country_list_command(self, args: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/otf/blacklisted-countries/', params=args)

    def inbound_blacklisted_country_list_command(self, args: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/blacklisted-countries/', params=args)

    def outbound_blacklisted_country_add_command(self, body: dict) -> list:
        return list(self._http_request(method='POST', url_suffix='/otf/blacklisted-countries/', params=body))

    def inbound_blacklisted_country_add_command(self, body: dict) -> dict:
        return self._http_request(method='POST', url_suffix='/protection-groups/blacklisted-countries/', params=body)

    def outbound_blacklisted_country_delete_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/otf/blacklisted-countries/', params=body,
                                  return_empty_response=True)

    def inbound_blacklisted_country_delete_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/protection-groups/blacklisted-countries/', params=body,
                                  return_empty_response=True)

    # host lists handlers

    def outbound_blacklisted_host_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/otf/blacklisted-hosts/', params=body)

    def outbound_whitelisted_host_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/otf/whitelisted-hosts/', params=body)

    def inbound_blacklisted_host_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/blacklisted-hosts/', params=body)

    def inbound_whitelisted_host_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/whitelisted-hosts/', params=body)

    # host addition/updates handlers

    def outbound_blacklisted_host_add_update_command(self, body: dict, op: str) -> dict:
        return self._http_request(method=op, url_suffix='/otf/blacklisted-hosts/', json_data=body,
                                  headers=merge_dicts(self._headers, {'Content-Type': 'application/json'}))

    def outbound_whitelisted_host_add_update_command(self, body: dict, op: str) -> dict:
        return self._http_request(method=op, url_suffix='/otf/whitelisted-hosts/', json_data=body,
                                  headers=merge_dicts(self._headers, {'Content-Type': 'application/json'}))

    def inbound_blacklisted_host_add_update_command(self, body: dict, op: str) -> dict:
        return self._http_request(method=op, url_suffix='/protection-groups/blacklisted-hosts/', json_data=body,
                                  headers=merge_dicts(self._headers, {'Content-Type': 'application/json'}))

    def inbound_whitelisted_host_add_update_command(self, body: dict, op: str) -> dict:
        return self._http_request(method=op, url_suffix='/protection-groups/whitelisted-hosts/', json_data=body,
                                  headers=merge_dicts(self._headers, {'Content-Type': 'application/json'}))

    # host deletion handlers

    def outbound_blacklisted_host_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/otf/blacklisted-hosts/', params=body,
                                  return_empty_response=True)

    def outbound_whitelisted_host_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/otf/whitelisted-hosts/', params=body,
                                  return_empty_response=True)

    def inbound_blacklisted_host_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/protection-groups/blacklisted-hosts/', params=body,
                                  return_empty_response=True)

    def inbound_whitelisted_host_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/protection-groups/whitelisted-hosts/', params=body,
                                  return_empty_response=True)

    # domain handlers

    def inbound_blacklisted_domain_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/blacklisted-domains/', params=body)

    def inbound_blacklisted_domain_add_command(self, body: dict) -> dict:
        return self._http_request(method='POST', url_suffix='/protection-groups/blacklisted-domains/', params=body)

    def inbound_blacklisted_domain_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/protection-groups/blacklisted-domains/', params=body,
                                  return_empty_response=True)

    # url handlers

    def inbound_blacklisted_url_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/blacklisted-urls/', params=body)

    def inbound_blacklisted_url_add_command(self, body: dict) -> dict:
        return self._http_request(method='POST', url_suffix='/protection-groups/blacklisted-urls/', params=body)

    def inbound_blacklisted_url_remove_command(self, body: dict) -> requests.Response:
        return self._http_request(method='DELETE', url_suffix='/protection-groups/blacklisted-urls/', params=body,
                                  return_empty_response=True)

    # protection group handlers

    def protection_group_list_command(self, body: dict) -> dict:
        return self._http_request(method='GET', url_suffix='/protection-groups/', params=body)

    def protection_group_patch_command(self, body: dict) -> dict:
        return self._http_request(method='PATCH', url_suffix='/protection-groups/', params=body)


''' HELPER FUNCTIONS '''


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
       Merges two dictionaries into one dictionary.

       :type dict1: ``dict``
       :param dict1: The first dictionary.

       :type dict2: ``dict``
       :param dict2: The second dictionary.

       :return: The merged dictionary.
       :rtype: ``dict``
    """
    return {**dict1, **dict2}


def init_commands_dict() -> dict:
    """
       Initializes the legal commands dictionary.

       :return: The commands dictionary.
       :rtype: ``dict``
    """

    inbound_blacklisted = {'direction': 'inbound', 'list_color': 'blacklist'}
    inbound_whitelisted = {'direction': 'inbound', 'list_color': 'whitelist'}
    outbound_blacklisted = {'direction': 'outbound', 'list_color': 'blacklist'}
    outbound_whitelisted = {'direction': 'outbound', 'list_color': 'whitelist'}

    return {
        # test module
        'test-module': {'func': test_module},

        # countries code list
        'na-aed-country-code-list': {'func': country_code_list_command},

        # outbound blacklisted countries
        'na-aed-outbound-blacklisted-countries-list': {'func': handle_country_list_commands,
                                                       'meta_data': outbound_blacklisted},
        'na-aed-outbound-blacklisted-countries-add': {'func': handle_country_addition_commands,
                                                      'meta_data': outbound_blacklisted},
        'na-aed-outbound-blacklisted-countries-remove': {'func': handle_country_deletion_commands,
                                                         'meta_data': outbound_blacklisted},

        # inbound blacklisted countries
        'na-aed-inbound-blacklisted-countries-list': {'func': handle_country_list_commands,
                                                      'meta_data': inbound_blacklisted},
        'na-aed-inbound-blacklisted-countries-add': {'func': handle_country_addition_commands,
                                                     'meta_data': inbound_blacklisted},
        'na-aed-inbound-blacklisted-countries-remove': {'func': handle_country_deletion_commands,
                                                        'meta_data': inbound_blacklisted},

        # outbound blacklisted hosts
        'na-aed-outbound-blacklisted-hosts-list': {'func': handle_host_list_commands,
                                                   'meta_data': outbound_blacklisted},
        'na-aed-outbound-blacklisted-hosts-add': {'func': handle_host_addition_and_replacement_commands,
                                                  'meta_data': merge_dicts(outbound_blacklisted, {'op': 'POST'})},

        'na-aed-outbound-blacklisted-hosts-replace': {'func': handle_host_addition_and_replacement_commands,
                                                      'meta_data': merge_dicts(outbound_blacklisted, {'op': 'PUT'})},
        'na-aed-outbound-blacklisted-hosts-remove': {'func': handle_host_deletion_commands,
                                                     'meta_data': outbound_blacklisted},

        # inbound blacklisted hosts
        'na-aed-inbound-blacklisted-hosts-list': {'func': handle_host_list_commands,
                                                  'meta_data': inbound_blacklisted},
        'na-aed-inbound-blacklisted-hosts-add': {'func': handle_host_addition_and_replacement_commands,
                                                 'meta_data': merge_dicts(inbound_blacklisted, {'op': 'POST'})},
        'na-aed-inbound-blacklisted-hosts-replace': {'func': handle_host_addition_and_replacement_commands,
                                                     'meta_data': merge_dicts(inbound_blacklisted, {'op': 'PUT'})},
        'na-aed-inbound-blacklisted-hosts-remove': {'func': handle_host_deletion_commands,
                                                    'meta_data': inbound_blacklisted},

        # outbound whitelisted hosts
        'na-aed-outbound-whitelisted-hosts-list': {'func': handle_host_list_commands,
                                                   'meta_data': outbound_whitelisted},
        'na-aed-outbound-whitelisted-hosts-add': {'func': handle_host_addition_and_replacement_commands,
                                                  'meta_data': merge_dicts(outbound_whitelisted, {'op': 'POST'})},
        'na-aed-outbound-whitelisted-hosts-replace': {'func': handle_host_addition_and_replacement_commands,
                                                      'meta_data': merge_dicts(outbound_whitelisted, {'op': 'PUT'})},
        'na-aed-outbound-whitelisted-hosts-remove': {'func': handle_host_deletion_commands,
                                                     'meta_data': outbound_whitelisted},

        # inbound whitelisted hosts
        'na-aed-inbound-whitelisted-hosts-list': {'func': handle_host_list_commands,
                                                  'meta_data': inbound_whitelisted},
        'na-aed-inbound-whitelisted-hosts-add': {'func': handle_host_addition_and_replacement_commands,
                                                 'meta_data': merge_dicts(inbound_whitelisted, {'op': 'POST'})},
        'na-aed-inbound-whitelisted-hosts-replace': {'func': handle_host_addition_and_replacement_commands,
                                                     'meta_data': merge_dicts(inbound_whitelisted, {'op': 'PUT'})},
        'na-aed-inbound-whitelisted-hosts-remove': {'func': handle_host_deletion_commands,
                                                    'meta_data': inbound_whitelisted},

        # inbound blacklisted domains
        'na-aed-inbound-blacklisted-domains-list': {'func': handle_domain_list_commands},
        'na-aed-inbound-blacklisted-domains-add': {'func': handle_domain_addition_commands},
        'na-aed-inbound-blacklisted-domains-remove': {'func': handle_domain_deletion_commands},

        # inbound blacklisted urls
        'na-aed-inbound-blacklisted-urls-list': {'func': handle_url_list_commands},
        'na-aed-inbound-blacklisted-urls-add': {'func': handle_url_addition_commands},
        'na-aed-inbound-blacklisted-urls-remove': {'func': handle_url_deletion_commands},

        # protection groups
        'na-aed-protection-groups-list': {'func': handle_protection_groups_list_commands},
        'na-aed-protection-groups-update': {'func': handle_protection_groups_update_commands},

    }


def objects_time_to_readable_time(list_of_objects: list, time_key: str) -> None:
    """

        Gets a list of objects with "time" key and
        Replaces the value of the field with a readable format and
        Convert all keys of a dictionary to snake_case.

       :type list_of_objects: ``list``
       :param list_of_objects: The list of objects to iterate.

       :type time_key: ``str``
       :param time_key: The time key field to change to date.

       :return: No data returned.
       :rtype: ``None``

    """
    for i, item in enumerate(list_of_objects):
        timestamp = item.get(time_key)
        if not timestamp:
            raise DemistoException("'time_key' argument is not valid")
        item[time_key] = timestamp_to_datestring(timestamp * 1000)
        list_of_objects[i] = snakify(item)


def deserialize_protection_groups(list_of_protection_groups: list) -> None:
    """

        Gets a list of objects (which represents the protection groups)
        deserializes them to a more human readable format.

        :type list_of_protection_groups: ``list``
        :param list_of_protection_groups: The list of protection groups to iterate.

        :return: No data returned.
        :rtype: ``None``

    """
    for item in list_of_protection_groups:
        active = item.get('active')
        item['active'] = True if active == 1 else False
        protection_level = item.get('protectionLevel')
        if protection_level == 1:
            item['protectionLevel'] = 'low'
        elif protection_level == 2:
            item['protectionLevel'] = 'medium'
        elif protection_level == 3:
            item['protectionLevel'] = 'high'
        if not protection_level:
            item['protectionLevel'] = 'global protection level'


def serialize_protection_groups(list_of_protection_groups: list) -> None:
    """

        Gets a list of objects (which represents the protection groups)
        serializes them to the format which the api expects.

        :type list_of_protection_groups: ``list``
        :param list_of_protection_groups: The list of protection groups to iterate.

        :return: No data returned.
        :rtype: ``None``

    """
    for item in list_of_protection_groups:
        active = item.get('active')
        if active:
            item['active'] = 1 if active == 'true' else 0
        protection_level = item.get('protectionLevel', '')
        if protection_level == 'low':
            item['protectionLevel'] = 1
        elif protection_level == 'medium':
            item['protectionLevel'] = 2
        elif protection_level == 'high':
            item['protectionLevel'] = 3
        elif protection_level == 'None':
            item['protectionLevel'] = 'None'

        profiling = item.get('profiling')
        if profiling:
            item['profiling'] = 1 if profiling == 'true' else 0


''' COMMAND FUNCTIONS '''


def test_module(client: Client, demisto_args: dict) -> str:
    """

        Tests API connectivity and authentication'
        Returning 'ok' indicates that the integration works like it is supposed to.
        Connection to the service is successful.
        Raises exceptions if something goes wrong.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: 'ok' if test passed, anything else will fail the test.
        :rtype: ``str``

    """
    try:
        client.country_code_list_command(demisto_args)
    except Exception as e:
        demisto.debug(f'Error: {str(e)}')
        if 'UNAUTHORIZED' in str(e) or 'invalidAuthToken' in str(e):
            raise DemistoException('Test failed, make sure API Key is correctly set.', exception=e)
        elif 'Error in API call' in str(e):
            raise DemistoException('Test failed, Error in API call', exception=e)
        else:
            raise DemistoException(f'Test failed, Please check your parameters. \n{str(e)}', exception=e)
    return 'ok'


def country_code_list_command(client: Client, demisto_args: dict) -> CommandResults:
    """

        Gets the countries codes and names.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains a dict of the countries codes and names.
        :rtype: ``CommandResults``

    """
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    limit = demisto_args.pop('limit', None)
    if limit:
        demisto_args['per_page'] = limit
    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    raw_result = client.country_code_list_command(demisto_args)
    countries_list = [{'country_name': item.get('name'), 'iso_code': item.get('country')} for item in
                      raw_result.get('countries', [])]
    readable_output = tableToMarkdown('Netscout AED Countries List',
                                      countries_list,
                                      removeNull=True,
                                      headerTransform=string_to_table_header)
    return CommandResults(
        outputs_prefix='NetscoutAED.Country',
        outputs_key_field='country_name',
        outputs=countries_list,
        raw_response=countries_list,
        readable_output=readable_output,

    )


def handle_country_list_commands(client: Client, demisto_args: dict,
                                 meta_data: dict) -> CommandResults:
    """

        Gets the countries from the inbound/outbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the countries list is outbound or inbound.

        :return: The command results which contains a dict of the outbound/inbound blacklisted countries.
        :rtype: ``CommandResults``

    """

    direction = meta_data.get('direction')
    remove_nulls_from_dictionary(demisto_args)
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    limit = demisto_args.pop('limit', None)
    if limit:
        demisto_args['per_page'] = limit
    demisto_args = camelize(demisto_args, '_', upper_camel=False)

    if direction == 'outbound':
        raw_result = client.outbound_blacklisted_country_list_command(demisto_args)
    else:  # inbound
        raw_result = client.inbound_blacklisted_country_list_command(demisto_args)

    name = list(raw_result.keys())[0]
    countries_list = copy.deepcopy(raw_result.get(name, []))
    objects_time_to_readable_time(countries_list, 'updateTime')
    table_header = string_to_table_header(name.replace('-', ' '))

    readable_output = tableToMarkdown(table_header, countries_list,
                                      headers=['country', 'update_time', 'annotation', 'pgid', 'cid'],
                                      headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix=f'NetscoutAED.{camelize_string(direction)}BlacklistCountry',
        outputs_key_field='country',
        outputs=countries_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_country_addition_commands(client: Client, demisto_args: dict,
                                     meta_data: dict) -> CommandResults:
    """

        Adds a country to the inbound/outbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the countries list is outbound or inbound.

        :return: The command results which contains a dict of the added outbound/inbound blacklisted countries.
        :rtype: ``CommandResults``

    """

    direction = meta_data.get('direction')
    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    countries_to_add = demisto_args.get('country')

    if not countries_to_add:
        raise DemistoException(
            f'You must provide country code in order to add it to the {direction} blacklisted list.')

    demisto_args['country'] = ','.join(argToList(countries_to_add))

    if direction == 'outbound':
        raw_result: Union[dict, list] = client.outbound_blacklisted_country_add_command(demisto_args)
        countries_list = list(copy.deepcopy(raw_result))

    else:  # inbound
        raw_result = client.inbound_blacklisted_country_add_command(demisto_args)
        countries_list = copy.deepcopy(raw_result.get('countries', [raw_result]))

    objects_time_to_readable_time(countries_list, 'updateTime')

    msg = f'Countries were successfully added to the {direction} blacklisted list\n'

    readable_output = msg + tableToMarkdown('Added Countries',
                                                   countries_list,
                                                   headers=['country', 'cid', 'pgid', 'update_time',
                                                            'annotation'],
                                                   headerTransform=string_to_table_header, removeNull=True)
    return CommandResults(
        outputs_prefix=f'NetscoutAED.{camelize_string(direction)}BlacklistCountry',
        outputs_key_field='country',
        outputs=countries_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_country_deletion_commands(client: Client, demisto_args: dict, meta_data: dict) -> str:
    """

        Removes a country from the inbound/outbound blacklistd list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the countries list is outbound or inbound.

        :return: A message which says that the countries were successfully deleted from the list.
        :rtype: ``str``

    """

    direction = meta_data.get('direction')
    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    countries_to_delete = demisto_args.get('country')
    if not countries_to_delete:
        raise DemistoException(
            f'You must provide country code in order to remove it from the {direction} blacklisted list.')

    demisto_args['country'] = ','.join(argToList(countries_to_delete))

    if direction == 'outbound':
        raw_result = client.outbound_blacklisted_country_delete_command(demisto_args)

    else:  # inbound
        raw_result = client.inbound_blacklisted_country_delete_command(demisto_args)

    if raw_result.status_code != 204:
        raise DemistoException('Api call should return no content status')

    return f'Countries were successfully removed from the {direction} blacklisted list'


def handle_host_list_commands(client: Client, demisto_args: dict,
                              meta_data: dict) -> CommandResults:
    """

        Gets the hosts from the inbound/outbound blacklisted/whitelisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the host list is
                          (outbound or inbound) and (blacklisted or whitelisted).

        :return: The command results which contains a dict of the outbound/inbound blacklisted/whitelisted hosts.
        :rtype: ``CommandResults``

    """

    direction = meta_data.get('direction')
    list_color = meta_data.get('list_color')
    remove_nulls_from_dictionary(demisto_args)
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    limit = demisto_args.pop('limit', None)
    if limit:
        demisto_args['per_page'] = limit
    demisto_args = camelize(demisto_args, '_', upper_camel=False)

    if direction == 'outbound':
        if list_color == 'blacklist':
            raw_result = client.outbound_blacklisted_host_list_command(demisto_args)
        else:  # whitelist
            raw_result = client.outbound_whitelisted_host_list_command(demisto_args)

    else:  # inbound
        if list_color == 'blacklist':
            raw_result = client.inbound_blacklisted_host_list_command(demisto_args)
        else:
            raw_result = client.inbound_whitelisted_host_list_command(demisto_args)

    name = list(raw_result.keys())[0]
    hosts_list = copy.deepcopy(raw_result.get(name, []))
    objects_time_to_readable_time(hosts_list, 'updateTime')
    table_header = string_to_table_header(name.replace('-', ' '))
    readable_output = tableToMarkdown(table_header, hosts_list,
                                      headers=['host_address', 'cid', 'pgid', 'update_time', 'annotation'],
                                      headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix=f'NetscoutAED.{camelize_string(direction)}{camelize_string(list_color)}Host',
        outputs_key_field='host_address',
        outputs=hosts_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_host_addition_and_replacement_commands(client: Client,
                                                  demisto_args: dict,
                                                  meta_data: dict) -> CommandResults:
    """

        Adds hosts to the inbound/outbound blacklisted/whitelisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the host list is
                          (outbound or inbound) and (blacklist or whitelist).

        :return: The command results which contains a dict of the added/replaced hosts in the
                 outbound/inbound blacklisted/whitelisted list.
        :rtype: ``CommandResults``

    """
    direction = meta_data.get('direction')
    list_color = meta_data.get('list_color')
    op = str(meta_data.get('op'))

    host_address = demisto_args.get('host_address')
    if not host_address:
        raise DemistoException(
            f'You must provide host in order to add/update him in the {direction} {list_color} list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, "_", upper_camel=False)
    demisto_args['hostAddress'] = argToList(host_address)

    if direction == 'outbound':
        if list_color == 'blacklist':
            raw_result = client.outbound_blacklisted_host_add_update_command(demisto_args, op)
        else:  # whitelist
            raw_result = client.outbound_whitelisted_host_add_update_command(demisto_args, op)

    else:  # inbound
        if list_color == 'blacklist':
            raw_result = client.inbound_blacklisted_host_add_update_command(demisto_args, op)
        else:
            raw_result = client.inbound_whitelisted_host_add_update_command(demisto_args, op)

    hosts_list = copy.deepcopy(raw_result.get('hosts', [raw_result]))

    msg_op = 'added to' if op == 'POST' else 'replaced in'

    msg = f'Hosts were successfully {msg_op} the {direction} {list_color} list\n'

    objects_time_to_readable_time(hosts_list, 'updateTime')

    readable_output = msg + tableToMarkdown('New Hosts',
                                                   hosts_list,
                                                   headers=['host_address', 'pgid', 'cid', 'update_time',
                                                            'annotation', ],
                                                   headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix=f'NetscoutAED.{camelize_string(direction)}{camelize_string(list_color)}Host',
        outputs_key_field='host_address',
        outputs=hosts_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_host_deletion_commands(client: Client, demisto_args: dict,
                                  meta_data: dict) -> str:
    """

        Removes hosts from the inbound/outbound blacklisted/whitelisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :type meta_data: ``dict``
        :param meta_data: The meta data which determines if the host list is
                          (outbound or inbound) and (blacklist or whitelist).

        :return: A message which says that the hosts were successfully deleted from the list.
        :rtype: ``str``

    """
    direction = meta_data.get('direction')
    list_color = meta_data.get('list_color')
    host_address = demisto_args.get('host_address')

    if not host_address:
        raise DemistoException(f'You must provide host in order to remove it from the {direction} {list_color} list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    demisto_args['hostAddress'] = ','.join(argToList(host_address))

    if direction == 'outbound':
        if list_color == 'blacklist':
            raw_result = client.outbound_blacklisted_host_remove_command(demisto_args)
        else:
            raw_result = client.outbound_whitelisted_host_remove_command(demisto_args)

    else:  # inbound
        if list_color == 'blacklist':
            raw_result = client.inbound_blacklisted_host_remove_command(demisto_args)
        else:
            raw_result = client.inbound_whitelisted_host_remove_command(demisto_args)

    if raw_result.status_code != 204:
        raise DemistoException('Api call should return no content status')

    return f'Hosts were successfully removed from the {direction} {list_color} list'


def handle_protection_groups_list_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Gets the list of protections groups.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains a list of the protection groups.
        :rtype: ``CommandResults``

    """
    remove_nulls_from_dictionary(demisto_args)
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    serialize_protection_groups([demisto_args])
    raw_result = client.protection_group_list_command(demisto_args)
    protection_group_list = copy.deepcopy(raw_result.get('protection-groups', []))
    deserialize_protection_groups(protection_group_list)
    objects_time_to_readable_time(protection_group_list, 'timeCreated')

    headers = ['name', 'pgid', 'protection_level', 'active', 'server_name', 'profiling', 'profiling_duration',
               'time_created', 'description']

    readable_output = tableToMarkdown('Protection Groups', protection_group_list, headers=headers,
                                      headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.Protection_Group',
        outputs_key_field='pgid',
        outputs=protection_group_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_protection_groups_update_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Updates the settings for one or more protection groups (pgid is required).

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains a dict of updated protection groups.
        :rtype: ``CommandResults``

    """

    pgid = demisto_args.get('pgid')
    if not pgid:
        raise DemistoException(
            'You must provide pgid in order to update the protection group.')
    if demisto_args.get('profiling') == 'true' and not demisto_args.get('profiling_duration'):
        raise DemistoException(
            'You must provide profiling duration when profiling is set to true.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    serialize_protection_groups([demisto_args])
    raw_result = client.protection_group_patch_command(demisto_args)
    protection_groups_list = copy.deepcopy(raw_result.get('protection-groups', [raw_result]))
    deserialize_protection_groups(protection_groups_list)
    objects_time_to_readable_time(protection_groups_list, 'timeCreated')
    headers = ['name', 'pgid', 'protection_level', 'active', 'server_name', 'profiling', 'profiling_duration',
               'time_created', 'description']
    msg = f'Successfully updated the protection group object with protection group id: {pgid}\n'

    readable_output = msg + tableToMarkdown('Protection Groups', protection_groups_list, headers=headers,
                                                   headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.Protection_Group',
        outputs_key_field='pgid',
        outputs=protection_groups_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_domain_list_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Gets the domains from the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains a list of the inbound blacklisted domains.
        :rtype: ``CommandResults``

    """

    remove_nulls_from_dictionary(demisto_args)
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    limit = demisto_args.pop('limit', None)
    if limit:
        demisto_args['per_page'] = limit
    demisto_args = camelize(demisto_args, "_", upper_camel=False)

    raw_result = client.inbound_blacklisted_domain_list_command(demisto_args)

    domains_list = copy.deepcopy(raw_result.get('blacklisted-domains', []))
    objects_time_to_readable_time(domains_list, 'updateTime')

    readable_output = tableToMarkdown('Blacklisted Domains', domains_list,
                                      headers=['domain', 'pgid', 'cid', 'update_time', 'annotation'],
                                      headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.InboundBlacklistDomain',
        outputs_key_field='domain',
        outputs=domains_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_domain_addition_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Adds the domains to the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains the added domains to the inbound blacklisted list.
        :rtype: ``CommandResults``

    """
    domain = demisto_args.get('domain')

    if not domain:
        raise DemistoException(
            'You must provide domain in order to add it to the inbound blacklisted list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    demisto_args['domain'] = ','.join(argToList(domain))

    raw_result = client.inbound_blacklisted_domain_add_command(demisto_args)
    domains_list = copy.deepcopy(raw_result.get('domains', [raw_result]))

    msg = 'Domains were successfully added to the inbound blacklisted list\n'

    objects_time_to_readable_time(domains_list, 'updateTime')

    readable_output = msg + tableToMarkdown('Added Domains', domains_list,
                                                   headers=['domain', 'pgid', 'cid', 'update_time', 'annotation'],
                                                   headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.InboundBlacklistDomain',
        outputs_key_field='domain',
        outputs=domains_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_domain_deletion_commands(client: Client, demisto_args: dict) -> str:
    """

        Removes domains from the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: A message which says that the domains were successfully deleted from the list.
        :rtype: ``str``

    """
    domain = demisto_args.get('domain')

    if not domain:
        raise DemistoException('You must provide domain in order to remove it from the inbound blacklisted list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    demisto_args['domain'] = ','.join(argToList(domain))

    raw_result = client.inbound_blacklisted_domain_remove_command(demisto_args)
    if raw_result.status_code != 204:
        raise DemistoException('Api call should return no content status')

    return 'Domains were successfully removed from the inbound blacklisted list'


def handle_url_list_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Gets the urls from the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains a list of the inbound blacklisted urls.
        :rtype: ``CommandResults``

    """
    remove_nulls_from_dictionary(demisto_args)
    query = demisto_args.pop('query', None)
    if query:
        demisto_args['q'] = query
    limit = demisto_args.pop('limit', None)
    if limit:
        demisto_args['per_page'] = limit
    demisto_args = camelize(demisto_args, '_', upper_camel=False)

    raw_result = client.inbound_blacklisted_url_list_command(demisto_args)

    urls_list = copy.deepcopy(raw_result.get('blacklisted-urls', []))
    objects_time_to_readable_time(urls_list, 'updateTime')

    readable_output = tableToMarkdown('Blacklisted URLs', urls_list,
                                      headers=['url', 'pgid', 'cid', 'update_time', 'annotation'],
                                      headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.InboundBlacklistUrl',
        outputs_key_field='url',
        outputs=urls_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_url_addition_commands(client: Client, demisto_args: dict) -> CommandResults:
    """

        Adds the urls to the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: The command results which contains the added urls to the inbound blacklisted list.
        :rtype: ``CommandResults``

    """
    url = demisto_args.get('url')

    if not url:
        raise DemistoException(
            'You must provide url in order to add it to the inbound blacklisted list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    demisto_args['url'] = ','.join(argToList(url))

    raw_result = client.inbound_blacklisted_url_add_command(demisto_args)
    urls_list = copy.deepcopy(raw_result.get('urls', [raw_result]))
    msg = 'Urls were successfully added to the inbound blacklisted list\n'

    objects_time_to_readable_time(urls_list, 'updateTime')

    readable_output = msg + tableToMarkdown('Added Urls', urls_list,
                                                   headers=['url', 'pgid', 'cid', 'update_time', 'annotation'],
                                                   headerTransform=string_to_table_header, removeNull=True)

    return CommandResults(
        outputs_prefix='NetscoutAED.InboundBlacklistUrl',
        outputs_key_field='url',
        outputs=urls_list,
        raw_response=raw_result,
        readable_output=readable_output,
    )


def handle_url_deletion_commands(client: Client, demisto_args: dict) -> str:
    """

        Removes urls from the inbound blacklisted list.

        :type client: ``Client``
        :param client: Client to use.

        :type demisto_args: ``dict``
        :param demisto_args: The demisto arguments.

        :return: A message which says that the urls were successfully deleted from the list.
        :rtype: ``str``

    """
    url = demisto_args.get('url')

    if not url:
        raise DemistoException('You must provide url in order to remove it from the inbound blacklisted list.')

    remove_nulls_from_dictionary(demisto_args)
    demisto_args = camelize(demisto_args, '_', upper_camel=False)
    demisto_args['url'] = ','.join(argToList(url))

    raw_result = client.inbound_blacklisted_url_remove_command(demisto_args)
    if raw_result.status_code != 204:
        raise DemistoException('Api call should return no content status')

    return 'Urls were successfully removed from the inbound blacklisted list'


''' MAIN FUNCTION '''


def main() -> None:
    try:
        params = demisto.params()
        base_url: str = urljoin(params.get('base_url', '').rstrip('/'), '/api/aed/v2')
        verify_certificate: bool = not params.get('insecure', False)
        proxy: bool = params.get('proxy', False)
        if not params.get('User') and not (api_token := params.get('User', {}).get('password')):
            raise DemistoException('Missing API Key. Fill in a valid key in the integration configuration.')
        commands = init_commands_dict()
        demisto_command = demisto.command()
        handle_proxy()
        client = Client(
            base_url=base_url,
            verify=verify_certificate,
            api_token=api_token,
            proxy=proxy)

        if not demisto_command or demisto_command not in commands:
            raise NotImplementedError(f'Command {demisto_command} is not implemented.')

        demisto.debug(f'Command being called is {demisto_command}')
        func_to_execute = dict_safe_get(commands, [demisto_command, 'func'])
        meta_data = dict_safe_get(commands, [demisto_command, 'meta_data'])
        demisto_args = demisto.args()
        results = func_to_execute(client, demisto_args, meta_data) if meta_data \
            else func_to_execute(client, demisto_args)
        return_results(results)

    # Log exceptions
    except Exception as e:
        return_error(f'Failed to execute {demisto.command()} command. Error: {str(e)}', error=e)


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
