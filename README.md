# AWS-COMPUTE-OPTIMIZER-EXPORT
AWS-COMPUTE-OPTIMIZER-EXPORT


## IAM ROLE 구성

### 1. IAM_ROLE_FOR_LAMBDA (MAIN-ACCOUNT lambda 함수 역할)
#### Trust Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
```
#### IAM Policy 
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": [
                "arn:aws:iam::*:role/IAM_ROLE_FOR_COMPUTE_OPTIMIZER"
            ]
        }
    ]
}
```

### 2. ACCOUNT-A (Assume Role 역할)
####  Trust Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<MAIN-ACCOUNT>:role/IAM_ROLE_FOR_LAMBDA"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
#### IAM Policy 
- ComputeOptimizerReadOnlyAccess
- AmazonS3FullAccess
- 
### 3. ACCOUNT-B (Assume Role 역할)
#### Trust Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<MAIN-ACCOUNT>:role/IAM_ROLE_FOR_LAMBDA"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
#### IAM Policy 
- ComputeOptimizerReadOnlyAccess
- AmazonS3FullAccess
