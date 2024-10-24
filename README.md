# AWS Compute Optimizer 내보내기 및 슬랙 알림

## 개요

이 프로젝트는 AWS Compute Optimizer 추천을 EC2 인스턴스, 오토 스케일링 그룹(ASG), EBS 볼륨 및 ECS 서비스에 대해 내보내고, 해당 추천을 CSV 형식으로 S3 버킷에 저장하는 두 개의 AWS Lambda 함수로 구성되어 있습니다. 내보내기가 완료되면 두 번째 Lambda 함수가 S3 버킷에서 생성된 CSV 파일을 검색하고, 이 파일들을 다운로드할 수 있는 사전 서명된 URL을 포함한 슬랙 알림을 전송합니다.

## 전제 조건

- AWS 계정: 역할을 가정하고 Compute Optimizer 및 S3 서비스에 접근할 수 있는 적절한 권한 필요.
- 슬랙 워크스페이스: 수신 웹훅 URL 설정 필요.
- Compute Optimizer에 대한 IAM 역할: 역할을 가정하고 필요한 리소스에 접근할 수 있는 권한 필요.

## 설정 방법

1. **AWS Lambda 함수**: 두 개의 Lambda 함수를 배포합니다:
   - **내보내기 함수**: Compute Optimizer 추천을 S3에 내보냅니다.
   - **알림 함수**: S3에서 내보낸 파일을 검색하고 슬랙 알림을 전송합니다.

2. **환경 변수**:
   - 알림 함수의 `HOOK_URL` 환경 변수를 슬랙 웹훅 URL로 설정합니다.

3. **IAM 역할**:
   - Lambda 함수가 STS, Compute Optimizer, S3에 접근하고 슬랙 메시지를 전송할 수 있는 필요한 IAM 권한을 가지고 있는지 확인합니다.

## 기능

### 1. 내보내기 함수

이 함수는 다음 작업을 수행합니다:

- 지정된 AWS 계정에서 역할을 가정합니다.
- 다음 서비스에 대한 Compute Optimizer 추천을 S3 버킷에 내보냅니다:
  - EC2 인스턴스
  - 오토 스케일링 그룹 (ASG)
  - EBS 볼륨
  - ECS 서비스
- 추천 사항은 지정된 S3 버킷의 구조화된 디렉토리에 CSV 형식으로 저장됩니다.

### 2. 알림 함수

이 함수는 다음 작업을 수행합니다:

- S3 버킷에서 내보낸 CSV 파일 목록을 검색합니다.
- 각 CSV 파일에 대해 다운로드할 수 있는 사전 서명된 URL을 생성합니다.
- 슬랙 블록 키트 형식으로 메시지를 구성하고, 웹훅 URL을 통해 지정된 슬랙 채널에 전송합니다.


## 사용 예시

1. 내보내기 함수를 호출하여 내보내기 프로세스를 시작합니다.
2. 내보내기가 완료되면 알림 함수를 호출하여 다운로드 링크가 포함된 슬랙 알림을 전송합니다.
3. 두 함수를 일정 간격으로 스케줄링 하여 자동화가 가능합니다.
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
