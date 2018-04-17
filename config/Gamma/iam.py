from awslambdacontinuousdelivery.tools.iam import (
    defaultAssumeRolePolicyDocument
  , oneClickCreateLogsPolicy
  )

from troposphere import Sub
from troposphere.iam import Role, Policy
from awacs.dynamodb import PutItem
import awacs.aws
import awacs.s3 as s3

def get_s3_access() -> Policy:
  statements = [
    awacs.aws.Statement(
      Action = [ s3.PutObject ],
      Effect = awacs.aws.Allow,
      Resource = [
        Sub("arn:aws:s3:${AWS::Region}:${AccountId}:iotweatherdata-gamma*") ]
    )
  ]
  policyDoc = awacs.aws.Policy( Statement = statements )
  return Policy( PolicyName = Sub("S3Access-${AWS::StackName}")
               , PolicyDocument = policyDoc
               )

def get_secret_manager() -> Policy:
  statements = [
    awacs.aws.Statement(
      Action = [ awacs.aws.Action("secretsmanager", "GetSecretValue") ],
      Effect = awacs.aws.Allow,
      Resource = [ "arn:aws:secretsmanager:*:*:secret:iot/prod*" ]
    )
  ]
  policyDoc = awacs.aws.Policy( Statement = statements )
  return Policy( PolicyName = Sub("SecretManagerAccess-${AWS::StackName}")
               , PolicyDocument = policyDoc
               )

def get_iam(ref_name: str) -> Role:
  assume = defaultAssumeRolePolicyDocument("lambda.amazonaws.com")
  return Role( ref_name
             , RoleName = ref_name
             , AssumeRolePolicyDocument = assume
             , Policies = [ oneClickCreateLogsPolicy()
                          , get_secret_manager()
                          , get_s3_access()
                          ]
             )

if __name__ == "__main__":
  print("For Testing only")
  secret = get_secret_manager()
  print(str(secret.to_dict()))
  role = get_iam("Test")
  print(str(role.to_dict()))
