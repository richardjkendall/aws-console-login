import logging
import os

from ddb import get_ddb_items

logger = logging.getLogger(__name__)

def check_role(groups, user, account, role):
  roles = get_roles(groups, user)

  role_okay = False

  for a, r in roles:
    if a == account and r == role:
      role_okay = True
  
  return role_okay


def get_roles(groups, user):
  roles = []
  
  group_user_combos = [("*", "*")]
  group_user_combos.append(("*", user))
  for group in groups:
    group_user_combos.append((group, "*"))

  for g, u in group_user_combos:
    logger.info(f"working on group={g} and user={u}")
    items = get_ddb_items(os.environ.get("TABLE_NAME"), group=g, user=u)
    print(items)
    for item in items:
      for role in item["roles"]:
        roles.append((role["account_id"], role["role_name"]))
  
  return roles