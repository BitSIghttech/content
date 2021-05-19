from typing import Tuple
import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

"""IMPORTS"""
import boto3
import base64
from datetime import datetime, date
from botocore.config import Config
from botocore.parsers import ResponseParserError
import urllib3.util

# Disable insecure warnings
urllib3.disable_warnings()

#
# """HELPER FUNCTIONS"""
# def aws_session(service='lambda', region=None, roleArn=None, roleSessionName=None, roleSessionDuration=None,
#                 rolePolicy=None):
#     kwargs = {}
#     config = CONFIG
#     command_config: Dict[str, Any] = {}
#     retries = demisto.getArg('retries')
#     if retries:
#         command_config['retries'] = dict(max_attempts=int(retries))
#     timeout = demisto.getArg('timeout')
#     if timeout:
#         (read_timeout, connect_timeout) = get_timeout(timeout)
#         command_config['read_timeout'] = read_timeout
#         command_config['connect_timeout'] = connect_timeout
#     if retries or timeout:
#         demisto.debug(f'Merging client config settings: {command_config}')
#         config = CONFIG.merge(Config(**command_config))
#     if roleArn and roleSessionName is not None:
#         kwargs.update({
#             'RoleArn': roleArn,
#             'RoleSessionName': roleSessionName,
#         })
#     elif AWS_ROLE_ARN and AWS_ROLE_SESSION_NAME is not None:
#         kwargs.update({
#             'RoleArn': AWS_ROLE_ARN,
#             'RoleSessionName': AWS_ROLE_SESSION_NAME,
#         })
#
#     if roleSessionDuration is not None:
#         kwargs.update({'DurationSeconds': int(roleSessionDuration)})
#     elif AWS_ROLE_SESSION_DURATION is not None:
#         kwargs.update({'DurationSeconds': int(AWS_ROLE_SESSION_DURATION)})
#
#     if rolePolicy is not None:
#         kwargs.update({'Policy': rolePolicy})
#     elif AWS_ROLE_POLICY is not None:
#         kwargs.update({'Policy': AWS_ROLE_POLICY})
#     if kwargs and not AWS_ACCESS_KEY_ID:
#
#         if not AWS_ACCESS_KEY_ID:
#             sts_client = boto3.client('sts', config=config, verify=VERIFY_CERTIFICATE,
#                                       region_name=AWS_DEFAULT_REGION)
#             sts_response = sts_client.assume_role(**kwargs)
#             if region is not None:
#                 client = boto3.client(
#                     service_name=service,
#                     region_name=region,
#                     aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
#                     aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
#                     aws_session_token=sts_response['Credentials']['SessionToken'],
#                     verify=VERIFY_CERTIFICATE,
#                     config=config
#                 )
#             else:
#                 client = boto3.client(
#                     service_name=service,
#                     region_name=AWS_DEFAULT_REGION,
#                     aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
#                     aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
#                     aws_session_token=sts_response['Credentials']['SessionToken'],
#                     verify=VERIFY_CERTIFICATE,
#                     config=config
#                 )
#     elif AWS_ACCESS_KEY_ID and AWS_ROLE_ARN:
#         sts_client = boto3.client(
#             service_name='sts',
#             aws_access_key_id=AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#             verify=VERIFY_CERTIFICATE,
#             config=config
#         )
#         kwargs.update({
#             'RoleArn': AWS_ROLE_ARN,
#             'RoleSessionName': AWS_ROLE_SESSION_NAME,
#         })
#         sts_response = sts_client.assume_role(**kwargs)
#         client = boto3.client(
#             service_name=service,
#             region_name=AWS_DEFAULT_REGION,
#             aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
#             aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
#             aws_session_token=sts_response['Credentials']['SessionToken'],
#             verify=VERIFY_CERTIFICATE,
#             config=config
#         )
#     else:
#         if region is not None:
#             client = boto3.client(
#                 service_name=service,
#                 region_name=region,
#                 aws_access_key_id=AWS_ACCESS_KEY_ID,
#                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                 verify=VERIFY_CERTIFICATE,
#                 config=config
#             )
#         else:
#             client = boto3.client(
#                 service_name=service,
#                 region_name=AWS_DEFAULT_REGION,
#                 aws_access_key_id=AWS_ACCESS_KEY_ID,
#                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                 verify=VERIFY_CERTIFICATE,
#                 config=config
#             )
#     return client


def parse_tag_field(tags_str):
    tags = []
    regex = re.compile(r'key=([\w\d_:.-]+),value=([ /\w\d@_,.\*-]+)', flags=re.I)
    for f in tags_str.split(';'):
        match = regex.match(f)
        if match is None:
            demisto.log('could not parse field: %s' % (f,))
            continue

        tags.append({
            'Key': match.group(1),
            'Value': match.group(2)
        })
    return tags


class DatetimeEncoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def parse_resource_ids(resource_id):
    id_list = resource_id.replace(" ", "")
    resource_ids = id_list.split(",")
    return resource_ids


def create_entry(title, data, ec):
    return {
        'ContentsFormat': formats['json'],
        'Type': entryTypes['note'],
        'Contents': data,
        'ReadableContentsFormat': formats['markdown'],
        'HumanReadable': tableToMarkdown(title, data) if data else 'No result were found',
        'EntryContext': ec
    }


"""MAIN FUNCTIONS"""


def get_function(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )
    obj = vars(client._client_config)
    kwargs = {'FunctionName': args.get('functionName')}
    if args.get('qualifier') is not None:
        kwargs.update({'Qualifier': args.get('qualifier')})

    response = client.get_function(**kwargs)
    func = response['Configuration']
    data = ({
        'FunctionName': func['FunctionName'],
        'FunctionArn': func['FunctionArn'],
        'Runtime': func['Runtime'],
        'Region': obj['_user_provided_options']['region_name'],
    })

    raw = json.loads(json.dumps(response, cls=DatetimeEncoder))
    if raw:
        raw.update({'Region': obj['_user_provided_options']['region_name']})

    ec = {'AWS.Lambda.Functions(val.FunctionArn === obj.FunctionArn)': raw}
    human_readable = tableToMarkdown('AWS Lambda Functions', data)
    return_outputs(human_readable, ec)


def list_functions(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )
    obj = vars(client._client_config)
    data = []
    output = []

    paginator = client.get_paginator('list_functions')
    for response in paginator.paginate():
        for function in response['Functions']:
            data.append({
                'FunctionName': function['FunctionName'],
                'FunctionArn': function['FunctionArn'],
                'Runtime': function['Runtime'],
                'LastModified': function['LastModified'],
                'Region': obj['_user_provided_options']['region_name'],
            })
            output.append(function)

    raw = json.loads(json.dumps(response, cls=DatetimeEncoder))
    if raw:
        raw.update({'Region': obj['_user_provided_options']['region_name']})

    ec = {'AWS.Lambda.Functions(val.FunctionArn === obj.FunctionArn)': raw}
    human_readable = tableToMarkdown('AWS Lambda Functions', data)
    return_outputs(human_readable, ec)


def list_aliases(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )

    data = []
    output = []
    kwargs = {'FunctionName': args.get('functionName')}
    if args.get('functionVersion') is not None:
        kwargs.update({'FunctionVersion': args.get('functionVersion')})

    paginator = client.get_paginator('list_aliases')
    for response in paginator.paginate(**kwargs):
        for alias in response['Aliases']:
            data.append({
                'AliasArn': alias['AliasArn'],
                'Name': alias['Name'],
                'FunctionVersion': alias['FunctionVersion'],
            })
            output.append(alias)
    try:
        raw = json.loads(json.dumps(output, cls=DatetimeEncoder))
    except ValueError as e:
        return_error('Could not decode/encode the raw response - {err_msg}'.format(err_msg=e))
    ec = {'AWS.Lambda.Aliases(val.AliasArn === obj.AliasArn)': raw}
    human_readable = tableToMarkdown('AWS Lambda Aliases', data)
    return_outputs(human_readable, ec)


def invoke(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )
    obj = vars(client._client_config)
    kwargs = {'FunctionName': args.get('functionName')}
    if args.get('invocationType') is not None:
        kwargs.update({'InvocationType': args.get('invocationType')})
    if args.get('logType') is not None:
        kwargs.update({'LogType': args.get('logType')})
    if args.get('clientContext') is not None:
        kwargs.update({'ClientContext': args.get('clientContext')})
    if args.get('payload') is not None:
        payload = args.get('payload')
        if (not isinstance(payload, str)) or (not payload.startswith('{') and not payload.startswith('[')):
            payload = json.dumps(payload)
        kwargs.update({'Payload': payload})
    if args.get('qualifier') is not None:
        kwargs.update({'Qualifier': args.get('qualifier')})
    response = client.invoke(**kwargs)
    data = ({
        'FunctionName': args.get('functionName'),
        'Region': obj['_user_provided_options']['region_name'],
    })
    if 'LogResult' in response:
        data.update({'LogResult': base64.b64decode(response['LogResult']).decode("utf-8")})  # type:ignore
    if 'Payload' in response:
        data.update({'Payload': response['Payload'].read().decode("utf-8")})  # type:ignore
    if 'ExecutedVersion' in response:
        data.update({'ExecutedVersion': response['ExecutedVersion']})  # type:ignore
    if 'FunctionError' in response:
        data.update({'FunctionError': response['FunctionError']})

    ec = {'AWS.Lambda.InvokedFunctions(val.FunctionName === obj.FunctionName)': data}
    human_readable = tableToMarkdown('AWS Lambda Invoked Functions', data)
    return_outputs(human_readable, ec)


def remove_permission(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )
    kwargs = {
        'FunctionName': args.get('functionName'),
        'StatementId': args.get('StatementId')
    }
    if args.get('Qualifier') is not None:
        kwargs.update({'Qualifier': args.get('Qualifier')})
    if args.get('RevisionId') is not None:
        kwargs.update({'RevisionId': args.get('RevisionId')})

    response = client.remove_permission(**kwargs)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        demisto.results('Permissions have been removed')


def get_account_settings(args, aws_client):
    client = aws_client.aws_session(
        service='lambda',
        region=args.get('region'),
        role_arn=args.get('roleArn'),
        role_session_name=args.get('roleSessionName'),
        role_session_duration=args.get('roleSessionDuration'),
    )
    obj = vars(client._client_config)
    response = client.get_account_settings()
    account_limit = response['AccountLimit']
    account_usage = response['AccountUsage']
    data = {
        'AccountLimit': {
            'TotalCodeSize': str(account_limit['TotalCodeSize']),
            'CodeSizeUnzipped': str(account_limit['CodeSizeUnzipped']),
            'CodeSizeZipped': str(account_limit['CodeSizeZipped']),
            'ConcurrentExecutions': str(account_limit['ConcurrentExecutions']),
            'UnreservedConcurrentExecutions': str(account_limit['UnreservedConcurrentExecutions'])
        },
        'AccountUsage': {
            'TotalCodeSize': str(account_usage['TotalCodeSize']),
            'FunctionCount': str(account_usage['FunctionCount'])
        }
    }
    try:
        raw = json.loads(json.dumps(response, cls=DatetimeEncoder))
    except ValueError as e:
        return_error('Could not decode/encode the raw response - {err_msg}'.format(err_msg=e))
    if raw:
        raw.update({'Region': obj['_user_provided_options']['region_name']})

    ec = {'AWS.Lambda.Functions(val.Region === obj.Region)': raw}
    human_readable = tableToMarkdown('AWS Lambda Functions', data)
    return_outputs(human_readable, ec)


"""TEST FUNCTION"""


def test_function(aws_client):
    client = aws_client.aws_session(service='lambda')
    response = client.list_functions()
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        demisto.results('ok')


def main():

    params = demisto.params()
    aws_default_region = params.get('defaultRegion')
    aws_role_arn = params.get('roleArn')
    aws_role_session_name = params.get('roleSessionName')
    aws_role_session_duration = params.get('sessionDuration')
    aws_role_policy = None
    aws_access_key_id = params.get('access_key')
    aws_secret_access_key = params.get('secret_key')
    verify_certificate = not params.get('insecure', True)
    timeout = params.get('timeout')
    retries = params.get('retries') or 5
    validate_params(aws_default_region, aws_role_arn, aws_role_session_name, aws_access_key_id,
                    aws_secret_access_key)
    aws_client = AWSClient(aws_default_region, aws_role_arn, aws_role_session_name, aws_role_session_duration,
                           aws_role_policy, aws_access_key_id, aws_secret_access_key, verify_certificate, timeout,
                           retries)
    try:
        if demisto.command() == 'test-module':
            test_function(aws_client)
        elif demisto.command() == 'aws-lambda-get-function':
            get_function(demisto.args(), aws_client)
        elif demisto.command() == 'aws-lambda-list-functions':
            list_functions(demisto.args(), aws_client)
        elif demisto.command() == 'aws-lambda-list-aliases':
            list_aliases(demisto.args(), aws_client)
        elif demisto.command() == 'aws-lambda-invoke':
            invoke(demisto.args(), aws_client)
        elif demisto.command() == 'aws-lambda-remove-permission':
            remove_permission(demisto.args(), aws_client)
        elif demisto.command() == 'aws-lambda-get-account-settings':
            get_account_settings(demisto.args(), aws_client)
    except ResponseParserError as e:
        return_error('Could not connect to the AWS endpoint. Please check that the region is valid.\n {error}'.format(
            error=type(e)))
    except Exception as e:
        return_error('Error has occurred in the AWS Lambda Integration: {error}\n {message}'.format(
            error=type(e), message=str(e)))

from AWSApiModule import *  # noqa: E402

# python2 uses __builtin__ python3 uses builtins
if __name__ in ("__builtin__", "builtins"):
    main()
