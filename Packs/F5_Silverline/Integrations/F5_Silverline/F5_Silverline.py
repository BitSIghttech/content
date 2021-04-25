import demistomock as demisto
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import
from CommonServerUserPython import *  # noqa

import requests
import traceback
from typing import Dict, Any

requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

BASE_URL = "/api/v1/ip_lists"
TABLE_HEADERS_GET_OBJECTS = ['ID', 'IP', 'Expires At', 'List Target', 'Created At', 'Updated At']


class Client(BaseClient):
    def __init__(self, base_url: str, verify: bool, headers: dict, proxy: bool):
        """
        Client to use in the F5_Silverline integration. Overrides BaseClient.

        Args:
            base_url (str): URL to access when doing an http request.
            verify (bool): Whether to check for SSL certificate validity.
            headers (dict): Headers to set when when doing an http request.
            proxy (bool): Whether the client should use proxies.
        """
        super().__init__(base_url=base_url, verify=verify, proxy=proxy)
        self._headers = headers

    def request_ip_objects(self, body: dict, method: str, url_suffix: str, params: dict, resp_type='json') -> Dict:
        """
        Makes an HTTP request to F5 Silverline API by the given arguments.
        Args:
            body (dict): The dictionary to send in a 'POST' request.
            method (str): HTTP request method (GET/POST/DELETE).
            url_suffix (str): The API endpoint.
            params (dict): URL parameters to specify the query.
            resp_type (str): Determines which data format to return from the HTTP request. The default is 'json'.
        """
        demisto.debug(f'current request is: method={method}, body={body}, url suffix={url_suffix},'
                      f'params={params}, resp_type={resp_type}')
        return self._http_request(method=method, json_data=body, url_suffix=url_suffix, params=params,
                                  headers=self._headers, resp_type=resp_type)


def test_module(client: Client) -> str:
    """
    Tests API connectivity and authentication. Does a GET request for this purpose.
    """
    try:
        client.request_ip_objects(body={}, method='GET', url_suffix='denylist/ip_objects', params={})
        message = 'ok'
    except DemistoException as e:
        if 'Unauthorized' in str(e):
            message = 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return message


def paging_args_to_params(page_size, page_number):
    """
    Returns the parameters to the HTTP request when using paging.
    """
    try:
        page_size = int(page_size)
        page_number = int(page_number)
    except ValueError:
        raise ValueError("page_number and page_size should be numbers")

    params = {'page[size]': page_size, 'page[number]': page_number}
    return params


def add_ip_objects_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    # TODO handle the bad_actor list_type
    """
    Adds a new IP object to the requested list type (denylist or allowlist).
    IP object includes an IP address (mandatory). Other fields are optional and have default values.
    Note: Human readable appears only if the HTTP request did not fail.
    """
    list_type = args.get('list_type')
    list_target = args.get('list_target', 'proxy-routed')
    ip_address = args.get('IP')
    mask = args.get('mask', '32')
    duration = int(args.get('duration', 0))
    note = args.get('note', "")
    tags = argToList(args.get('tags', []))
    url_suffix = f'{list_type}/ip_objects'

    body = {"list_target": list_target, "data": {"id": "", "type": "ip_objects",
                                                 "attributes": {"mask": mask, "ip": ip_address, "duration": duration},
                                                 "meta": {"note": note, "tags": tags}}}

    human_readable = f"IP object with IP address: {ip_address} created successfully to the {list_type} list."
    client.request_ip_objects(body=body, method='POST', url_suffix=url_suffix, params={}, resp_type='content')
    return CommandResults(readable_output=human_readable)


def delete_ip_objects_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    # TODO handle the bad_actor list_type
    """
    Deletes an exist IP object from the requested list type (denylist or allowlist) by its object id (mandatory).
    Note: Human readable appears only if the HTTP request did not fail.
    """
    list_type = args.get('list_type')
    object_id = args.get('object_id')
    url_suffix = f'{list_type}/ip_objects/{object_id}'
    client.request_ip_objects(body={}, method='DELETE', url_suffix=url_suffix, params={}, resp_type='content')
    human_readable = f"IP object with ID: {object_id} deleted successfully from the {list_type} list."
    return CommandResults(readable_output=human_readable)


def get_ip_objects_list_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    # TODO handle the bad_actor list_type
    list_type = args.get('list_type')
    object_ids = argToList(args.get('object_id'))
    page_number = args.get('page_number')
    page_size = args.get('page_size')
    url_suffix = f'{list_type}/ip_objects'
    params = {}

    is_paging = False
    if page_number and page_size:
        params = paging_args_to_params(page_size, page_number)
        is_paging = True

    if not object_ids:
        # in case the user wants to get all the IP objects and not specific ones
        response = client.request_ip_objects(body={}, method='GET', url_suffix=url_suffix, params=params)
        outputs = response.get('data')
        human_results = parse_get_ip_object_list_results(response)
    else:
        human_results, outputs = get_ip_objects_by_ids(client, object_ids, list_type, params)

    human_readable = tableToMarkdown('F5 Silverline IP Objects', human_results, TABLE_HEADERS_GET_OBJECTS,
                                     removeNull=True)

    if not human_results and is_paging:
        human_readable = "No results were found. Please try to run the command without page_number and page_size to " \
                         "get all the IP objects that exist."

    return CommandResults(
        readable_output=human_readable,
        outputs_prefix='F5Silverline.IPObjectList',
        outputs_key_field='id',
        outputs=outputs
    )


def get_ip_objects_by_ids(client: Client, object_ids: list, list_type: str, params: dict):
    """
    In case the user requests one or more specific IP objects (by their object_id). For each id we make a separate
    HTTP request (the API does not support list of ids).
    """
    human_results = []
    outputs = []
    for object_id in object_ids:
        url_suffix = f'{list_type}/ip_objects'
        url_suffix = '/'.join([url_suffix, object_id])
        res = client.request_ip_objects(body={}, method='GET', url_suffix=url_suffix, params=params)
        outputs.append(res.get('data'))
        human_results.append(parse_get_ip_object_list_results(res)[0])
    return human_results, outputs


def parse_get_ip_object_list_results(results: Dict):
    """
    Parsing the API response after requesting the IP object list. Parsing maps the important fields that will appear
    as the human readable output.
    """
    parsed_results = []
    results_data = results.get('data')  # type: ignore
    demisto.debug(f"response is {results_data}")
    if isinstance(results_data, dict):
        # in case the response consist only single ip object, the result is a dict and not a list, so we want to handle
        # those cases in the same way
        results_data = [results_data]
    for ip_object in results_data:  # type: ignore
        if ip_object:
            parsed_results.append({
                'ID': ip_object.get('id'),
                'IP': ip_object.get('attributes').get('ip'),
                'Expires At': ip_object.get('attributes').get('expires_at'),
                'List Target': ip_object.get('attributes').get('list_target'),
                'Created At': ip_object.get('meta').get('created_at'),
                'Updated At': ip_object.get('meta').get('updated_at')
            })
    return parsed_results


def main() -> None:
    params = demisto.params()
    access_token = params.get('token')
    base_url = urljoin(params.get('url'), BASE_URL)
    verify_certificate = not params.get('insecure', False)
    proxy = params.get('proxy', False)

    demisto.debug(f'Command being called is {demisto.command()}')
    try:
        headers: Dict = {"X-Authorization-Token": access_token, "Content-Type": 'application/json'}

        client = Client(
            base_url=base_url,
            verify=verify_certificate,
            headers=headers,
            proxy=proxy)

        if demisto.command() == 'test-module':
            return_results(test_module(client))

        elif demisto.command() == 'f5-silverline-ip-objects-list':
            return_results(get_ip_objects_list_command(client, demisto.args()))

        elif demisto.command() == 'f5-silverline-ip-object-add':
            return_results(add_ip_objects_command(client, demisto.args()))

        elif demisto.command() == 'f5-silverline-ip-object-delete':
            return_results(delete_ip_objects_command(client, demisto.args()))
        else:
            raise NotImplementedError(f'{demisto.command()} is not an existing F5 Silverline command')

    except Exception as e:
        demisto.error(traceback.format_exc())
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
