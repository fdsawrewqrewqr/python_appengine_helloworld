import cgi
import webapp2
import urllib
import datetime
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import db


JINJA_ENVIRONMENT=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

				
MAIN_PAGE_FOOTER_TEMPLATE="""\
<html>
	<body>
		<form action="/sign?%s" method="post">
			<div><textarea name="content" rows="3" cols="60"></textarea></div>
			<div><input type="submit" value="Sign Guestbook"></div>
		</form>
		<hr>
		<form>Guestbook name: <input value="%s" name="guestbook_name">
		<input type="submit" value="switch"></form>
	</body>
</html>
"""

class Greeting(db.Model):
	"""Models and individual entry with author, content, and data."""
	author=db.StringProperty()
	content=db.StringProperty(multiline=True)
	date=db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""
	return db.Key.from_path('Guestbook',guestbook_name or 'default_tuestbook')
		
class MainPage(webapp2.RequestHandler):
	def get(self):
		guestbook_name=self.request.get('guestbook_name')
		greetings_query=Greeting.all().ancestor(guestbook_key(guestbook_name)).order('-date')
		greetings=greetings_query.fetch(10)
		
		if users.get_current_user():
			url = users.create_logout_url(self.request.url)
			url_linktext="Logout"
		else:
			url=users.create_login_url(self.request.url)
			url_linktext="Login"
			
		template_values={'greetings':greetings, 'url':url,'url_linktext':url_linktext,}
		
		template=JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))
			
		
		
class Guestbook(webapp2.RequestHandler):
	def post(self):
		guestbook_name=self.request.get('guestbook_name')
		greeting=Greeting(parent=guestbook_key(guestbook_name))
		
		if users.get_current_user():
			greeting.author=users.get_current_user().nickname()
			
		greeting.content=self.request.get('content')
		greeting.put()
		
		query_params={'guestbook_name':guestbook_name}
		self.redirect('/?'+urllib.urlencode(query_params))
							
		
app = webapp2.WSGIApplication([('/', MainPage),('/sign',Guestbook)],debug=True)