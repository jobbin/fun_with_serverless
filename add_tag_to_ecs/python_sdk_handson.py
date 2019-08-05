
# pip install aliyun-python-sdk-core, oss2, aliyun-python-sdk-actiontrail, aliyun-python-sdk-ram
# pip install aliyun-python-sdk-sts, aliyun-fc2, aliyun-python-sdk-vpc, aliyun-python-sdk-ecs

# coding=utf-8
import time
import oss2
import json
import fc2
from aliyunsdkcore.client import AcsClient
from aliyunsdksts.request.v20150401.GetCallerIdentityRequest import GetCallerIdentityRequest
from aliyunsdkram.request.v20150501.CreateRoleRequest import CreateRoleRequest
from aliyunsdkram.request.v20150501.GetRoleRequest import GetRoleRequest
from aliyunsdkram.request.v20150501.AttachPolicyToRoleRequest import AttachPolicyToRoleRequest
from aliyunsdkactiontrail.request.v20171204.CreateTrailRequest import CreateTrailRequest
from aliyunsdkactiontrail.request.v20171204.StartLoggingRequest import StartLoggingRequest
from aliyunsdkactiontrail.request.v20171204.DescribeTrailsRequest import DescribeTrailsRequest
from aliyunsdkram.request.v20150501.ListPoliciesForRoleRequest import ListPoliciesForRoleRequest


#########################################
# APIコールのClientの作成
#########################################
REGION = "ap-northeast-1"
ACCESS_KEY_ID = "< Your Access Key ID >"
ACCESS_KEY_SECRET = "< Your Secret Key >"
client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)


#########################################
# AccountIDの取得
#########################################
request = GetCallerIdentityRequest()
request.set_accept_format('json')
response = json.loads(client.do_action_with_exception(request))

# ACCOUNT_IDの確認
ACCOUNT_ID = response["AccountId"]
print("AccountId = " , ACCOUNT_ID)


#########################################
# OSS
# 　ActionTrail用のOSS Bucketの作成
#########################################
OSS_BUCKET = "action-trail-log" + "-" +  ACCOUNT_ID
OSS_ENDPOINT = "oss-ap-northeast-1.aliyuncs.com"

bucket = oss2.Bucket(oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET), OSS_ENDPOINT, OSS_BUCKET)
bucket.create_bucket(permission=oss2.BUCKET_ACL_PRIVATE,
                     input=oss2.models.BucketCreateConfig(oss2.BUCKET_STORAGE_CLASS_STANDARD))

# 作成したOSS Bucketの確認
bucket_info = bucket.get_bucket_info()
print('name: ' + bucket_info.name)
print('storage class: ' + bucket_info.storage_class)
print('creation date: ' + bucket_info.creation_date)


###############################################################
# RAM Role
# 　ActionTrail用のRAM Roleの作成、信頼関係の付与、RAM Policyの付与
###############################################################

# 変数の準備
ACTION_TRAIL_ROLE　= "AliyunActionTrailDefaultRole"

# 指定したRoleの存在確認、存在しない場合はエラー表示
# 想定結果: Error:EntityNotExist.Role
request = GetRoleRequest()
request.set_accept_format('json')
request.set_RoleName(ACTION_TRAIL_ROLE)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# Roleの作成、信頼関係の付与
request = CreateRoleRequest()
request.set_accept_format('json')
request.set_RoleName(ACTION_TRAIL_ROLE)
request.set_AssumeRolePolicyDocument("{\"Statement\":[{\"Action\": \"sts:AssumeRole\",\"Effect\": \"Allow\",\"Principal\": {\"Service\": [\"actiontrail.aliyuncs.com\"]}}],\"Version\": \"1\"}")

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["Role"], indent=4, sort_keys=True))

# 作成したRoleにPolicyの付与
request = AttachPolicyToRoleRequest()
request.set_accept_format('json')
request.set_PolicyType("System")
request.set_PolicyName("AliyunOSSFullAccess")
request.set_RoleName(ACTION_TRAIL_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# 指定したRoleにPolicyを付与したかの確認
request = ListPoliciesForRoleRequest()
request.set_accept_format('json')
request.set_RoleName("AliyunActionTrailDefaultRole")

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))


###############################################################
# ActionTrail
# 　ActionTrailの作成、OSS Bucketの設定、ActionTraioの有効化
###############################################################

# 変数の準備
ACTION_TRAIL = "audit-trail" # Your ActionTrail
ACTION_TRAIL_ROLE = "AliyunActionTrailDefaultRole"

# ActionTrailの確認
request = DescribeTrailsRequest()
request.set_accept_format('json')

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# ActionTrailの作成
request = CreateTrailRequest()
request.set_accept_format('json')
request.set_Name(ACTION_TRAIL)
request.set_OssBucketName(OSS_BUCKET)
request.set_RoleName(ACTION_TRAIL_ROLE)

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))

# ActionTrailの確認、デフォルトはStatus無効(Fresh)になっている
request = DescribeTrailsRequest()
request.set_accept_format('json')

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["TrailList"][0], indent=4, sort_keys=True))

# ActionTrailの有効化
request = StartLoggingRequest()
request.set_accept_format('json')
request.set_Name(ACTION_TRAIL)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# ActionTrailのStatusの確認、Statusが Fresh -> Enable
request = DescribeTrailsRequest()
request.set_accept_format('json')

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["TrailList"][0], indent=4, sort_keys=True))


###############################################################
# RAM Role
# 　Function Compute用のRAM Roleの作成、信頼関係の付与、RAM Policyの付与
###############################################################

# 変数の準備
FC_ROLE = "fc-role"

# Roleの作成、信頼関係の付与
request = CreateRoleRequest()
request.set_accept_format('json')
request.set_RoleName(FC_ROLE)
request.set_AssumeRolePolicyDocument("{\"Statement\":[{\"Action\": \"sts:AssumeRole\",\"Effect\": \"Allow\",\"Principal\": {\"Service\": [\"fc.aliyuncs.com\"]}}],\"Version\": \"1\"}")

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["Role"], indent=4, sort_keys=True))

# 作成したRoleにPolicy(AliyunOSSFullAccess)の付与
request = AttachPolicyToRoleRequest()
request.set_accept_format('json')
request.set_PolicyType("System")
request.set_PolicyName("AliyunOSSFullAccess")
request.set_RoleName(FC_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# 作成したRoleにPolicy(AliyunECSFullAccess)の付与
request.set_PolicyName("AliyunECSFullAccess")

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# 指定したRoleにPolicyを付与したかの確認
request = ListPoliciesForRoleRequest()
request.set_accept_format('json')
request.set_RoleName("AliyunActionTrailDefaultRole")

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response, indent=4, sort_keys=True))


###############################################################
# Function Compute
# 　Serviceの作成、Functionの作成、OSS Triggerの作成
###############################################################

# 変数の準備
FC_ENDPOINT = "https://" + ACCOUNT_ID + "." + REGION + ".fc.aliyuncs.com" # Function Compute Endpoint
ROLE_ARN = "acs:ram::"+ ACCOUNT_ID +":role/fc-role" # Function Compute Role ARN
FC_SERVICE = "test-fun" # Function Compute Service Name
FC_FUNCTION = "fc_function" # Function Compute Function Name

# FC Clientの作成
fc_client = fc2.Client(
    endpoint=FC_ENDPOINT,
    accessKeyID=ACCESS_KEY_ID,
    accessKeySecret=ACCESS_KEY_SECRET
    )

# FC Serviceの作成
service = fc_client.create_service(serviceName=FC_SERVICE, role=ROLE_ARN)

response = fc_client.list_services()
for service in response.data["services"]:
    print("Function compute : ", service["serviceName"])

# FC Functionの作成
response = fc_client.create_function(
                                    FC_SERVICE, 
                                    FC_FUNCTION, 
                                    'python3', 
                                    'index.handler', 
                                    codeZipFile = 'code.zip',
                                    environmentVariables = {'TAG_NAME': 'Owner'}
                                    )
# 確認
print(json.dumps(response.data, indent=4, sort_keys=True))

# OSS Triggerの作成
OSS_TRIGGER = "oss-trigger"
OSS_TRIGGER_CONFIG = {"events": ["oss:ObjectCreated:PutObject"]}
OSS_SOURCE_ARN = "acs:oss:ap-northeast-1:" + ACCOUNT_ID + ":" + OSS_BUCKET
TRIGGER_TYPE = "oss"
INVOCATION_ROLE = 'acs:ram::'+ ACCOUNT_ID + ':role/aliyunosseventnotificationrole'

response = fc_client.create_trigger(
                                    FC_SERVICE, 
                                    FC_FUNCTION, 
                                    OSS_TRIGGER, 
                                    TRIGGER_TYPE,
                                    OSS_TRIGGER_CONFIG, 
                                    OSS_SOURCE_ARN, 
                                    INVOCATION_ROLE
                                )

# 確認
print(json.dumps(response.data, indent=4, sort_keys=True))


###############################################################
#　　　　　　　　　　　　　　　動作確認フェーズ                       #
###############################################################

###############################################################
# VPC
#   VPC, VSwitchの作成
###############################################################
"""
# 既存のVPCの取得
request = DescribeVpcsRequest()
request.set_accept_format('json')

response = json.loads(client.do_action_with_exception(request))

for vpc in response["Vpcs"]["Vpc"]:
  print(vpc["VpcId"] +  ' | ' + vpc["VpcName"]  +  ' | ' +  str(vpc["IsDefault"]))
  print(str(vpc["VSwitchIds"]))
  print("\n")
"""

# VPCの作成
from aliyunsdkvpc.request.v20160428.CreateVpcRequest import CreateVpcRequest

request = CreateVpcRequest()
request.set_accept_format('json')
response = json.loads(client.do_action_with_exception(request))

# 確認
VPC_ID = response["VpcId"]
print(VPC_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# VSwithの作成
from aliyunsdkvpc.request.v20160428.CreateVSwitchRequest import CreateVSwitchRequest

# 変数の準備
CIRDER_BLOCK = "172.16.100.0/24"
ZONE_ID = "ap-northeast-1a"

request = CreateVSwitchRequest()
request.set_accept_format('json')
request.set_CidrBlock(CIRDER_BLOCK)
request.set_VpcId(VPC_ID)
request.set_ZoneId(ZONE_ID)

response = json.loads(client.do_action_with_exception(request))

# 確認
VSWITCH_ID = response["VSwitchId"]
print("VSWITCH_ID : " + VSWITCH_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))


###############################################################
# ECS
#   Security Group, ECS Instanceの作成
###############################################################
"""
# Security groupの取得
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupsRequest import DescribeSecurityGroupsRequest

VPC_ID = "vpc-***********"
request = DescribeSecurityGroupsRequest()
request.set_accept_format('json')
request.set_VpcId(VPC_ID)

response =  json.loads(client.do_action_with_exception(request))
"""

# Security Groupの作成
from aliyunsdkecs.request.v20140526.CreateSecurityGroupRequest import CreateSecurityGroupRequest

request = CreateSecurityGroupRequest()
request.set_accept_format('json')
request.set_VpcId(VPC_ID)
response = json.loads(client.do_action_with_exception(request))

# 確認
SECURITY_GROUP_ID = response["SecurityGroupId"]
print("SECURITY_GROUP_ID : " , SECURITY_GROUP_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

# ECS Instanceの作成
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest

# 変数の準備
IMAGE_ID = "ubuntu_18_04_64_20G_alibase_20190624.vhd"
INSTANCE_TYPE = "ecs.t5-lc1m1.small"

request = RunInstancesRequest()
request.set_accept_format('json')
request.set_ImageId(IMAGE_ID)
request.set_InstanceType(INSTANCE_TYPE)
request.set_SecurityGroupId(SECURITY_GROUP_ID)
request.set_VSwitchId(VSWITCH_ID)
request.set_ZoneId(ZONE_ID)

# 確認
# ECS Instanceが作成されてから, Tagをつけられるまで何秒間のタイムラグがある
response = json.loads(client.do_action_with_exception(request))
INSTANCE_ID = response["InstanceIdSets"]["InstanceIdSet"][0]
print("INSTANCE_ID :  ", INSTANCE_ID)
print("\n")
print(json.dumps(response, indent=4, sort_keys=True))

from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
request = DescribeInstancesRequest()
request.set_accept_format('json')
request.set_InstanceIds('["' + INSTANCE_ID + '"]')

response = json.loads(client.do_action_with_exception(request))
print(json.dumps(response["Instances"]["Instance"][0]["Tags"], indent=4, sort_keys=True))


#################################################################################
#                       リソース削除フェーズ
# 　StopInstanceRequest -> DeleteInstanceRequest -> DeleteSecurityGroupRequest
#   DeleteSecurityGroupRequest -> DeleteVSwitchRequest ->  DeleteVpcRequest
#   DetachPolicyFromRoleRequest -> DeleteRoleRequest
#   DeleteTrailRequest
#   (OSS)delete_object -> delete_bucket
##################################################################################

###############################################################
# ECS
#   ECS,Security Groupの削除
#   ※ ECS Instanceは停止の状態ではないと、削除できない
###############################################################

# ECS Insatanceの停止
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest

request = StopInstanceRequest()
request.set_accept_format('json')
request.set_InstanceId(INSTANCE_ID)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# ECS Insatanceの削除
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest

request = DeleteInstanceRequest()
request.set_accept_format('json')
request.set_InstanceId(INSTANCE_ID)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# Security Groupの削除
from aliyunsdkecs.request.v20140526.DeleteSecurityGroupRequest import DeleteSecurityGroupRequest

request = DeleteSecurityGroupRequest()
request.set_accept_format('json')
request.set_SecurityGroupId(SECURITY_GROUP_ID)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))


###############################################################
# VPC
#   VPC, VSwitchの削除
###############################################################

# VSwitchの削除
from aliyunsdkvpc.request.v20160428.DeleteVSwitchRequest import DeleteVSwitchRequest

request = DeleteVSwitchRequest()
request.set_accept_format('json')
request.set_VSwitchId(VSWITCH_ID)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# VPCの削除
from aliyunsdkvpc.request.v20160428.DeleteVpcRequest import DeleteVpcRequest

request = DeleteVpcRequest()
request.set_accept_format('json')
request.set_VpcId(VPC_ID)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))


###############################################################
# Function Compute
#   OSS Trigger,FC Function, FC Serviceの削除
#
# RAM Role
#   RoleのPolicyのDetach, Role削除
###############################################################

# OSS Triggerの削除
response = fc_client.delete_trigger(FC_SERVICE, FC_FUNCTION, OSS_TRIGGER)
print("Function Compute Trigger : ", response)

# FC Functionの削除
response = fc_client.delete_function(FC_SERVICE, FC_FUNCTION)
print("Function Compute Function : ", response)

# FC Serviceの削除
response = fc_client.delete_service(FC_SERVICE)
print("Function Compute Service : ", response)

# FC Roleから AliyunOSSFullAccess, AliyunECSFullAccess をDetach
from aliyunsdkram.request.v20150501.DetachPolicyFromRoleRequest import DetachPolicyFromRoleRequest

request = DetachPolicyFromRoleRequest()
request.set_accept_format('json')
request.set_PolicyType("System")
request.set_PolicyName("AliyunOSSFullAccess")
request.set_RoleName(FC_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

request.set_PolicyName("AliyunECSFullAccess")
response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# FC Roleの削除
from aliyunsdkram.request.v20150501.DeleteRoleRequest import DeleteRoleRequest

request = DeleteRoleRequest()
request.set_accept_format('json')
request.set_RoleName(FC_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

###############################################################
# ActionTrail
#   Trailの削除
#
# RAM Role
#   RoleのPolicyのDetach, Role削除
###############################################################
# ActionTrailの削除
from aliyunsdkactiontrail.request.v20171204.DeleteTrailRequest import DeleteTrailRequest

request = DeleteTrailRequest()
request.set_accept_format('json')
request.set_Name(ACTION_TRAIL)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# [Role] AliyunActionTrailDefaultRole から AliyunOSSFullAccess をDetach
request = DetachPolicyFromRoleRequest()
request.set_accept_format('json')
request.set_PolicyType("System")
request.set_PolicyName("AliyunOSSFullAccess")
request.set_RoleName(ACTION_TRAIL_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

# [Role] AliyunActionTrailDefaultRole の削除
request = DeleteRoleRequest()
request.set_accept_format('json')
request.set_RoleName(ACTION_TRAIL_ROLE)

response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))

###############################################################
# OSS
#   OSS Object, OSS Bucketの削除
###############################################################

# OSS Objectの削除
bucket = oss2.Bucket(oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET), OSS_ENDPOINT, OSS_BUCKET)

for obj in oss2.ObjectIterator(bucket):
    list = obj.key.split("/")
    oss_object = list[-1]
    response = bucket.delete_object(obj.key)
    print("Delete OSS Object ",oss_object, " , Status Code : ", response.status)
    # 出力例: Delete OSS Object  HelloWorld.py  :  204

# OSS Bucketの削除
response = bucket.delete_bucket()
print("Delete OSS Bucket ",OSS_BUCKET, " , Status Code : ", response.status)