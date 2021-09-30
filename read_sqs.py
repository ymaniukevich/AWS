import boto3
import json
import time
import requests

#AWX variable
AwxUrl=""
AwxToken = ""
AwxInventoryName="ALL"
AwxInitialTemplateType="workflow_job_templates"
AwxInitialTemplateName="Initial workflow"
timeout=10

#SQS variable
SqsName = ''
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
    print(iad_tags)
    print(len(event_messages))
    print(event_messages)
    
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


#read_sqs(MaxNumberOfMessages)
event_messages = [{'limit': 'wkdssapalweb-i-0a7d7b2039ab21ad8', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apactun', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0a7d7b2039ab21ad8', 'instance_ip': '172.29.5.12'}}, {'limit': 'wkmsceudlpps-i-05672bc0237c4e9c0', 'extra_vars': {'iad_platform': 'msc', 'iad_region': 'eu', 'iad_environment': 'dev', 'iad_component': 'multiservice_cluster_eks_left', 'instance_name': 'wkmsceudlpps-i-05672bc0237c4e9c0', 'instance_ip': '10.6.79.210'}}, {'limit': 'wkfrreuqlpps-i-0d4c1ddf92f832cbc', 'extra_vars': {'iad_platform': 'frr', 'iad_region': 'eu', 'iad_environment': 'qa', 'iad_component': 'multiservice_cluster_right', 'instance_name': 'wkfrreuqlpps-i-0d4c1ddf92f832cbc', 'instance_ip': '10.7.5.53'}}, {'limit': 'wkdssapalweb-i-0d1b9cc5037563464', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0d1b9cc5037563464', 'instance_ip': '172.29.4.106'}}, {'limit': 'wkpsdinatl-i-07c7640dc393b50e8', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-07c7640dc393b50e8', 'instance_ip': '172.20.20.166'}}, {'limit': 'wkdssapalsd-i-094d97fab20289b75', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'seas', 'instance_name': 'wkdssapalsd-i-094d97fab20289b75', 'instance_ip': '172.29.4.33'}}, {'limit': 'wkpsdieuglspooler-i-07ebc09eb9e7128b5', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'eu', 'iad_environment': 'grumpy', 'iad_component': 'app', 'instance_name': 'wkpsdieuglspooler-i-07ebc09eb9e7128b5', 'instance_ip': '172.140.135.255'}}, {'limit': 'wkpsdinatl-i-05df61781b79d6e1d', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-05df61781b79d6e1d', 'instance_ip': '172.20.20.56'}}, {'limit': 'wkfrreuqlpps-i-081e40b686d7205ea', 'extra_vars': {'iad_platform': 'frr', 'iad_region': 'eu', 'iad_environment': 'qa', 'iad_component': 'multiservice_cluster_right', 'instance_name': 'wkfrreuqlpps-i-081e40b686d7205ea', 'instance_ip': '10.7.4.96'}}, {'limit': 'wkdssapalweb-i-0600666bc8e327faf', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0600666bc8e327faf', 'instance_ip': '172.29.5.147'}}, {'limit': 'wkfrreuqlpps-i-0c2b3f9f3b686727b', 'extra_vars': {'iad_platform': 'frr', 'iad_region': 'eu', 'iad_environment': 'qa', 'iad_component': 'multiservice_cluster_right', 'instance_name': 'wkfrreuqlpps-i-0c2b3f9f3b686727b', 'instance_ip': '10.7.4.105'}}, {'limit': 'wkdssnaclseas-i-01ba0c35ba1e46e1e', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'na', 'iad_environment': 'cte', 'iad_component': 'seas', 'instance_name': 'wkdssnaclseas-i-01ba0c35ba1e46e1e', 'instance_ip': '172.28.59.129'}}, {'limit': 'wkdssapalweb-i-0878ecb59ed72cc7c', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0878ecb59ed72cc7c', 'instance_ip': '172.29.5.47'}}, {'limit': 'wkpsdinatl-i-0ec23a97287d6efdf', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-0ec23a97287d6efdf', 'instance_ip': '172.20.10.254'}}, {'limit': 'wkdssapalweb-i-08736efa866e8a450', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-08736efa866e8a450', 'instance_ip': '172.29.5.83'}}, {'limit': 'wkpsdinatl-i-0c47898d6b6f6e828', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-0c47898d6b6f6e828', 'instance_ip': '172.20.10.254'}}, {'limit': 'wkdssapalweb-i-0cb13ec00b4d84325', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apactun', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0cb13ec00b4d84325', 'instance_ip': '172.29.5.186'}}, {'limit': 'wkmsceudlpps-i-0144e97361dfb03a2', 'extra_vars': {'iad_platform': 'msc', 'iad_region': 'eu', 'iad_environment': 'dev', 'iad_component': 'multiservice_cluster_eks_left', 'instance_name': 'wkmsceudlpps-i-0144e97361dfb03a2', 'instance_ip': '10.6.75.253'}}, {'limit': 'wkpsdieuglspooler-i-0b9e923bf49650fda', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'eu', 'iad_environment': 'grumpy', 'iad_component': 'app', 'instance_name': 'wkpsdieuglspooler-i-0b9e923bf49650fda', 'instance_ip': '172.140.131.147'}}, {'limit': 'wkpsdinatl-i-0a5251eb92a354803', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-0a5251eb92a354803', 'instance_ip': '172.20.20.13'}}, {'limit': 'wkcchiqnaslcpe-i-0fd9bc977f0532ca6', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'na', 'iad_environment': 'dev2', 'iad_component': 'cpe', 'instance_name': 'wkcchiqnaslcpe-i-0fd9bc977f0532ca6', 'instance_ip': '172.28.63.166'}}, {'limit': 'wkdssapalnorad-i-08048965a287bbcde', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'norad', 'instance_name': 'wkdssapalnorad-i-08048965a287bbcde', 'instance_ip': '172.29.7.20'}}, {'limit': 'wkpsdinatl-i-065e792c49313f731', 'extra_vars': {'iad_platform': 'psdi', 'iad_region': 'na', 'iad_environment': 'taldvl', 'iad_component': 'puc', 'instance_name': 'wkpsdinatl-i-065e792c49313f731', 'instance_ip': '172.20.10.40'}}, {'limit': 'wkdssapalweb-i-0d1f1780e03017645', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0d1f1780e03017645', 'instance_ip': '172.29.5.111'}}, {'limit': 'wkiadeugllonzk-i-0b45b477893663e13', 'extra_vars': {'iad_platform': 'iad', 'iad_region': 'eu', 'iad_environment': 'geo', 'iad_component': 'zookeeper_tf12', 'instance_name': 'wkiadeugllonzk-i-0b45b477893663e13', 'instance_ip': '10.184.78.151'}}, {'limit': 'wkdssapalweb-i-054bd07df43fd0c58', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apacsb', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-054bd07df43fd0c58', 'instance_ip': '172.29.5.17'}}, {'limit': 'wkfrreuqlpps-i-087eba9c3f54cdefe', 'extra_vars': {'iad_platform': 'frr', 'iad_region': 'eu', 'iad_environment': 'qa', 'iad_component': 'multiservice_cluster_right', 'instance_name': 'wkfrreuqlpps-i-087eba9c3f54cdefe', 'instance_ip': '10.7.5.63'}}, {'limit': 'wkdssapalweb-i-0599f1f7be46a1165', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apactun', 'iad_component': 'web', 'instance_name': 'wkdssapalweb-i-0599f1f7be46a1165', 'instance_ip': '172.29.4.125'}}, {'limit': 'wkdssapalsd-i-08b5f1593121bb68d', 'extra_vars': {'iad_platform': 'dss', 'iad_region': 'apac', 'iad_environment': 'apactun', 'iad_component': 'seas', 'instance_name': 'wkdssapalsd-i-08b5f1593121bb68d', 'instance_ip': '172.29.4.217'}}]

for _ in event_messages:
    job_url = run_awx_template(AwxUrl, AwxToken, AwxInitialTemplateType, AwxInitialTemplateName, _, timeout)
    time.sleep(120)