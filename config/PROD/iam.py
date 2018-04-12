from awslambdacontinuousdelivery.tools.iam import (
    defaultAssumeRolePolicyDocument
  , oneClickCreateLogsPolicy
  )

from troposphere.iam import Role
from awacs.aws import Action, Allow, Policy, Statement


def get_secret_manager() -> Policy:
  return Policy(
    Statement = [
      Statement(
        Effect = Allow,
        Action = [ Action("secretsmanager:GetSecretValue") ],
        Resource = [ "arn:aws:secretsmanager:::secret/iot/prod*" ],
      ),
    ],
  )

def get_iam(ref_name: str) -> Role:
  assume = defaultAssumeRolePolicyDocument("lambda.amazonaws.com")
  return Role( ref_name
             , RoleName = ref_name
             , AssumeRolePolicyDocument = assume
             , Policies = [oneClickCreateLogsPolicy(), get_secret_manager()]
             )
