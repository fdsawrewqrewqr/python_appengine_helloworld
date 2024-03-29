import cgi
import webapp2
import urllib
import datetime

from google.appengine.api import users
from google.appengine.ext import db

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
		self.response.write('<html><body>')
		guestbook_name=self.request.get('guestbook_name')
		greetings=db.GqlQuery("SELECT * FROM Greeting WHERE ANCESTOR IS :1 ORDER BY date DESC LIMIT 10",guestbook_key(guestbook_name))
		
		for greeting in greetings:
			if greeting.author:
				self.response.write('<b>%s</b> wrote:' % greeting.author)
			else:
				self.response.write('An anonymous person wrote:')
			self.response.write('<blockquote>%s</blockquote>'%cgi.escape(greeting.content))			 
				
		sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
		self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % (sign_query_params, cgi.escape(guestbook_name)))
		
		
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