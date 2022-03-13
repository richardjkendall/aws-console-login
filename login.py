import urllib, json, sys
import requests 
import boto3 

sts_connection = boto3.client("sts")

def generate_console_url(account_id, role):
  assumed_role_object = sts_connection.assume_role(
    RoleArn=f"arn:aws:iam::{account_id}:role/{role}",
    RoleSessionName="AssumeRoleSession",
  )
  url_credentials = {}
  url_credentials["sessionId"] = assumed_role_object.get("Credentials").get("AccessKeyId")
  url_credentials["sessionKey"] = assumed_role_object.get("Credentials").get("SecretAccessKey")
  url_credentials["sessionToken"] = assumed_role_object.get("Credentials").get("SessionToken")
  json_string_with_temp_credentials = json.dumps(url_credentials)

  request_parameters = "?Action=getSigninToken"
  request_parameters += "&SessionDuration=43200"
  request_parameters += "&Session=" + urllib.parse.quote_plus(json_string_with_temp_credentials)
  request_url = "https://signin.aws.amazon.com/federation" + request_parameters
  r = requests.get(request_url)
  # Returns a JSON document with a single element named SigninToken.
  signin_token = json.loads(r.text)

  # Step 5: Create URL where users can use the sign-in token to sign in to 
  # the console. This URL must be used within 15 minutes after the
  # sign-in token was issued.
  request_parameters = "?Action=login" 
  request_parameters += "&Issuer=ConsoleLogin" 
  request_parameters += "&Destination=" + urllib.parse.quote_plus("https://console.aws.amazon.com/")
  request_parameters += "&SigninToken=" + signin_token["SigninToken"]
  request_url = "https://signin.aws.amazon.com/federation" + request_parameters

  # return final URL
  return request_url