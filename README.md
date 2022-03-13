# aws-console-login
Tool to generate AWS console login links.

It uses a DynamoDB table to look up entitlements based on group membership and username.

It should sit behind an authenticating proxy which sets the following headers:

```
x-remote-user-groups: the groups the user belongs to
x-remote-user: the username of the user
```
