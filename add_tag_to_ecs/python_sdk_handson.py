# pip install aliyun-python-sdk-core
# pip install oss2
# pip install aliyun-python-sdk-actiontrail
# pip install aliyun-python-sdk-ram
# pip install aliyun-python-sdk-sts

# coding=utf-8
import time
import oss2
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdksts.request.v20150401.GetCallerIdentityRequest import GetCallerIdentityRequest
from aliyunsdkram.request.v20150501.CreateRoleRequest import CreateRoleRequest
from aliyunsdkram.request.v20150501.GetRoleRequest import GetRoleRequest
from aliyunsdkram.request.v20150501.AttachPolicyToRoleRequest import AttachPolicyToRoleRequest
from aliyunsdkactiontrail.request.v20171204.CreateTrailRequest import CreateTrailRequest
from aliyunsdkactiontrail.request.v20171204.StartLoggingRequest import StartLoggingRequest
from aliyunsdkactiontrail.request.v20171204.DescribeTrailsRequest import DescribeTrailsRequest
from aliyunsdkram.request.v20150501.ListPoliciesForRoleRequest import ListPoliciesForRoleRequest


ENDPOINT = "oss-ap-northeast-1.aliyuncs.com"
REGION = "ap-northeast-1"
ACCESS_KEY_ID = "< Your Access Key ID >"
ACCESS_KEY_SECRET = "< Your Secret Key >"
ACTION_TRAIL = "< Your ActionTrail >"
ACTION_TRAIL_ROLE = "AliyunActionTrailDefaultRole"

#########################################
# APIコールのClientの作成
#########################################
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
OSS_BUCKET = "trail-test-jobbin" + "-" +  ACCOUNT_ID

bucket = oss2.Bucket(oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET), ENDPOINT, OSS_BUCKET)
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

# 指定したRoleの存在確認、存在しない場合はエラー表示
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

# 作成したRoleの確認
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


##############################
# ActionTrail
# 　ActionTrailの作成、OSS Bucketの設定、ActionTraioの有効化
##############################

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