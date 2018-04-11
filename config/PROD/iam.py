from awslambdacontinuousdelivery.tools.iam import (
    defaultAssumeRolePolicyDocument
  , oneClickCreateLogsPolicy
  )

from troposphere.iam import Role

def get_iam(ref_name: str) -> Role:
  assume = defaultAssumeRolePolicyDocument("lambda.amazonaws.com")
  return Role( ref_name
             , RoleName = ref_name
             , AssumeRolePolicyDocument = assume
             , Policies = [oneClickCreateLogsPolicy()]
             )
