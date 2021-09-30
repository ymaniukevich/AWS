import boto3
import json
import time
import requests

#AWX variable
AwxUrl="https://awx-iad.wkautomation.net"
AwxToken = "SWJymmhUtBfChaPlpXeiYxD1uXWnjU"
AwxInventoryName="ALL"
AwxInitialTemplateType="workflow_job_templates"
AwxInitialTemplateName="Initial workflow"
timeout=10

#SQS variable
SqsName = 'iad-na-prod-awx_handler_dead_letter_queue'
MaxNumberOfMessages = 10

event_messages = []
iad_tags = {}
list_of_skipping_component = ['import','gaimport']

boto3.setup_default_session(profile_name='iad_prod')
sqs = boto3.resource('sqs', region_name ='us-east-2')


def read_sqs(MaxNumberOfMessages):
    queue = sqs.get_queue_by_name(QueueName=SqsName)
    messages = queue.receive_messages(MaxNumberOfMessages=MaxNumberOfMessages, WaitTimeSeconds=2)
    count = 0
    while len(messages)>0:
        for message in messages:
            count += 1
            print(count)
            body = json.loads(message.body)
            environment = body['extra_vars']['iad_environment']
            component = body['extra_vars']['iad_component']
            dict_key = environment+component
            create_iad_items = {'iad_environment' : environment,
                                'iad_component': component}
            iad_tags[dict_key] = create_iad_items
            # Confition whether re-install this component
            if component not in list_of_skipping_component:
               event_messages.append(body)
            messages = queue.receive_messages(MaxNumberOfMessages=MaxNumberOfMessages)

    return iad_tags, event_messages



def run_awx_template(awx_url, awx_token, awx_initial_template_type, awx_initial_template_name, message_body, request_timeout):
    awx_templates_info = requests.get("{0}/api/v2/{1}".format(awx_url, awx_initial_template_type),
                                      headers={'Authorization': 'Bearer {0}'.format(awx_token),
                                               'Content-Type': 'application/json'}, timeout=request_timeout).json()['results']

    awx_template_id = next(_['id'] for _ in awx_templates_info if _[
                           'name'] == awx_initial_template_name)

    awx_launch_template = requests.post('{0}/api/v2/{1}/{2}/launch/'.format(awx_url, awx_initial_template_type, awx_template_id),
                                        json=message_body,
                                        headers={
                                            'Authorization': 'Bearer {0}'.format(awx_token),
                                            'Content-Type': 'application/json'}, timeout=request_timeout).json()
    print(awx_launch_template['url'])
    return awx_launch_template['url']



iad_tags, event_messages = read_sqs(MaxNumberOfMessages)

for _ in event_messages:
    job_url = run_awx_template(AwxUrl, AwxToken, AwxInitialTemplateType, AwxInitialTemplateName, _, timeout)
    time.sleep(120)