from flask import Flask, request, abort, render_template, Response
from markupsafe import escape
from datetime import datetime, timezone
import json
import hashlib

# What host are we working with?
def getHost():
   return request.host_url.split('/')[2]

# Passwords are stored in passwords.json, in the following format:
# {
#    "targetHostname": {
#      "value": "valueOrHash",
#      "type": "clear" # 'clear' indicates cleartext. Anything else takes the sha256 digest.
#    }
#    ...
# }

passwords = {}
with open('passwords.json', 'r') as f:
   passwords = json.loads(f.read())

def auth(host, password):
   if passwords[host]['type'] == 'clear':
      print('Clear', host, password, passwords[host]['value'])
      return password == passwords[host]['value']
   else:
      hash = hashlib.sha256()
      hash.update(password.encode())
      return hash.hexdigest() == passwords[host]['value']

def getPassword():
   return password[getHost()]

# Convenience for reading file
def get_lines():
   try:
      with open(getHost(), 'r') as stream:
         return list(map(lambda x: json.loads(x), stream.readlines()))
   except:
      return []

# Setup Flask app
app = Flask(__name__)

@app.route("/rss", methods=['GET'])
def rss():
   return Response(render_template('rss.xml', posts=get_lines()), mimetype='application/rss+xml')

@app.route("/text", methods=['GET'])
def text():
   return render_template('posts.html', posts=list(reversed(get_lines())))

@app.route('/post', methods=['GET', 'POST'])
def receive_post():
   if request.method == 'POST':
      newPost = {
         'body': escape(request.form['content']),
         'time': datetime.now(tz=timezone.utc).isoformat()
      }
      body = newPost['body'].replace('\r', '<br />').replace('\n', '')

      if not auth(getHost(), request.form['password']):
         return render_template('form.html', success=False, post=body)
      with open(getHost(), "a") as stream:
         stream.writelines([f'{json.dumps(newPost)}\n'])

      return render_template('form.html', success=True, post=body)
   else:
      return render_template('form.html', post=None)
