import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime


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
    
    
    now = datetime.now()
    formatted_date = now.strftime('/%Y/%m/%d')
    
    for i in accountIds:
        accountId, s3_key_prefix = next(iter(i.items()))
        token=getToken(accountId)
        
        
        compute_optimizer_client = boto3.client('compute-optimizer',aws_access_key_id=token["aws_access_key_id"],
        aws_secret_access_key=token["aws_secret_access_key"],
        aws_session_token=token["aws_session_token"]
        );
        
        s3_client = boto3.client('s3',aws_access_key_id=token["aws_access_key_id"],
        aws_secret_access_key=token["aws_secret_access_key"],
        aws_session_token=token["aws_session_token"]
        );
        
        
        
        try:
            bucket_name ='tidesquare-compute-optimizer'
            
            ec2_export_response = compute_optimizer_client.export_ec2_instance_recommendations(
                s3DestinationConfig={
                    'bucket': bucket_name,
                    'keyPrefix': s3_key_prefix+str(formatted_date)+'/EC2'
            },
            fileFormat='Csv'
            )
            
            asg_export_response = compute_optimizer_client.export_auto_scaling_group_recommendations(
                s3DestinationConfig={
                    'bucket': bucket_name,
                    'keyPrefix': s3_key_prefix+str(formatted_date)+'/ASG'
            },
            fileFormat='Csv'
            )
            
            ebs_export_response = compute_optimizer_client.export_ebs_volume_recommendations(
                s3DestinationConfig={
                    'bucket': bucket_name,
                    'keyPrefix': s3_key_prefix+str(formatted_date)+'/EBS'
            },
            fileFormat='Csv'
            )
            
            ecs_export_response = compute_optimizer_client.export_ecs_service_recommendations(
                s3DestinationConfig={
                    'bucket': bucket_name,
                    'keyPrefix': s3_key_prefix+str(formatted_date)+'/ECS'
            },
            fileFormat='Csv'
            )
            # rds_export_response = compute_optimizer_client.export_rds_database_recommendations(
            #     s3DestinationConfig={
            #         'bucket': bucket_name,
            #         'keyPrefix': s3_key_prefix+str(formatted_date)+'/RDS'
            # },
            # fileFormat='Csv'
            # )
            
            
        
        except ClientError as e:
            print(e)
