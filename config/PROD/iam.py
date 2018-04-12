from awslambdacontinuousdelivery.tools.iam import (
    defaultAssumeRolePolicyDocument
  , oneClickCreateLogsPolicy
  )

from troposphere import Sub
from troposphere.iam import Role, Policy
from awacs.aws import Action, Allow, Statement
import awacs.aws

def get_secret_manager() -> Policy:
  statements = [
    Statement(
      Action = [ Action("secretsmanager:GetSecretValue") ],
      Effect = Allow,
      Resource = [ "arn:aws:secretsmanager:::secret/iot/prod*" ]
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
             , Policies = [oneClickCreateLogsPolicy(), get_secret_manager()]
             )

if __name__ == "__main__":
  print("For Testing only")
  print(get_iam("Test"))
