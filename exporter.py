import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import urllib3

HOOK_URL=os.getenv('HOOK_URL')
http = urllib3.PoolManager();

def get_ssm_parameters_role(accountId):
    ssm_client = boto3.client('ssm');
    
    IAM_ROLE_ARN=ssm_client.get_parameters(Names=[SSM_PARAMETER_NAME])['Parameters'];
    
    value=IAM_ROLE_ARN[0]['Value']
    # using json.loads()
    # convert dictionary string to dictionary
    res = json.loads(value)
    
    print("IAM_ROLE_ARN : "+res[accountId])
    return res[accountId]
def getToken(accountId):
    SESSION_KEY={
    "aws_access_key_id":"",
        "aws_secret_access_key":"",
        "aws_session_token":""
    }
    sts_client=boto3.client('sts');
        #get session to target aws account.
        
    response = sts_client.assume_role(
        RoleArn='arn:aws:iam::'+str(accountId)+':role/IAM_ROLE_FOR_COMPUTE_OPTIMIZER',
        RoleSessionName="assume-role"
        )    

    SESSION_KEY["aws_access_key_id"]=response['Credentials']['AccessKeyId']
    SESSION_KEY["aws_secret_access_key"]=response['Credentials']['SecretAccessKey']
    SESSION_KEY["aws_session_token"]=response['Credentials']['SessionToken']
    
    return SESSION_KEY;

def lambda_handler(event, context):
    accountIds=[{'<ACCOUNT-A>':'ACCOUNT-A-Alias'},{'<ACCOUNT-B>':'ACCOUNT-B-Alias'}]
    compute_svc=['ASG','EBS','EC2','ECS']
    
    now = datetime.now()
    formatted_date = now.strftime('/%Y/%m/%d')
    
    
    for i in accountIds:
        accountId, s3_key_prefix = next(iter(i.items()))
        token=getToken(accountId)
        s3_client = boto3.client('s3');
        
        slack_block = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": s3_key_prefix +" 계정"
                    }
                }
            ]

        for svc in compute_svc:
            try:
                bucket_name ='tidesquare-compute-optimizer'
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=s3_key_prefix+formatted_date+'/'+svc+'/compute-optimizer/'+accountId+'/'
                    )
                for i in response['Contents'] :
                    if '.csv' in i['Key']:
                        s3_url = s3_client.generate_presigned_url('get_object',
                        Params={'Bucket': bucket_name,
                        'Key': i['Key']},
                        ExpiresIn=3600)
                        blocks = {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "<"+s3_url+"|"+svc+" export download>"
                            }
                        }
                        slack_block.append(blocks);
            except ClientError as e:
                print(e)
        
        msg={ "blocks": slack_block }
        print(msg)
        encoded_msg = json.dumps(msg).encode("utf-8");
        resp = http.request("POST", HOOK_URL, body=encoded_msg);
