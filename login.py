from distutils.command.config import config
import urllib, json, logging
import requests 
import boto3 


logger = logging.getLogger(__name__)

sts_connection = boto3.client("sts")

def get_caller_id():
  r = sts_connection.get_caller_identity()
  return r

def get_caller_id_for_specific_id(assumed_role_object):
  new_session = boto3.Session(
    aws_access_key_id = assumed_role_object.get("Credentials").get("AccessKeyId"),
    aws_secret_access_key = assumed_role_object.get("Credentials").get("SecretAccessKey"),
    aws_session_token = assumed_role_object.get("Credentials").get("SessionToken")
  )
  sts = new_session.client("sts", region_name="ap-southeast-2")
  r = sts.get_caller_identity()
  return r

def assume_role(account_id, role):
  assumed_role_object = sts_connection.assume_role(
    RoleArn=f"arn:aws:iam::{account_id}:role/{role}",
    RoleSessionName="AssumeRoleSession",
  )
  return assumed_role_object

def generate_console_url(assumed_role_object):
  logger.info(f"Getting console URL...")
  logger.info(f"Assumed role, {assumed_role_object}")
  url_credentials = {}
  url_credentials["sessionId"] = assumed_role_object.get("Credentials").get("AccessKeyId")
  url_credentials["sessionKey"] = assumed_role_object.get("Credentials").get("SecretAccessKey")
  url_credentials["sessionToken"] = assumed_role_object.get("Credentials").get("SessionToken")

  logger.info("Getting signin token")
  aws_federated_signin_endpoint = "https://ap-southeast-2.signin.aws.amazon.com/federation"
  r = requests.get(
    aws_federated_signin_endpoint,
    params = {
      "Action": "getSigninToken",
      "SessionDuration": "43200",
      "Session": json.dumps(url_credentials)
    }
  )
  logger.info("Got token for signin")
  
  # Returns a JSON document with a single element named SigninToken.
  signin_token = json.loads(r.text)

  # Step 5: Create URL where users can use the sign-in token to sign in to 
  # the console. This URL must be used within 15 minutes after the
  # sign-in token was issued.
  request_parameters = "?Action=login" 
  request_parameters += "&Issuer=ConsoleLogin" 
  request_parameters += "&Destination=" + urllib.parse.quote_plus("https://console.aws.amazon.com/")
  request_parameters += "&SigninToken=" + signin_token["SigninToken"]
  request_url = aws_federated_signin_endpoint + request_parameters

  # return final URL
  return request_url