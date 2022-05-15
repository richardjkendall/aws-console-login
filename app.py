import logging
import os, sys

from flask import Flask, render_template
from flask_cors import CORS
from security import secured
from roles import get_roles, check_role
from login import generate_console_url, get_caller_id

app = Flask(__name__)
CORS(app)

# set logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
logger = logging.getLogger(__name__)

if not os.environ.get("TABLE_NAME"):
  logger.error("TABLE_NAME not found")
  sys.exit(1)

@app.route("/")
@secured
def index(username, groups):
  roles = get_roles(groups=groups, user=username)
  caller_id = get_caller_id()
  return render_template(
    "index.html", 
    roles=roles, 
    user=username, 
    id_user=caller_id["UserId"],
    id_account=caller_id["Account"],
    id_arn=caller_id["Arn"]
  )

@app.route("/login/<string:account>/<string:role>")
@secured
def console_bounce(username, groups, account, role):
  okay = check_role(
    groups=groups,
    user=username,
    account=account,
    role=role
  )
  if okay:
    try:
      url = generate_console_url(account, role)
      return render_template("login.html", url=url, account=account, role=role)
    except:
      return render_template("error.html")
  else:
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")