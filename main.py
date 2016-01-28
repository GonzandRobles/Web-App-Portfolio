import os
import jinja2
import webapp2

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


DEFAULT_WALL = 'Public'

def wall_key(wall_name = DEFAULT_WALL):
	"""This will create a datastore key"""
	return ndb.Key('Wall', wall_name)
  

class CommentContainer(ndb.Model):
	"""This function contains the name, the content and date of the comments"""
	name = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
	"""This handler process the request, manipulates data and define a response to be returned to the client"""
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class MainPage(Handler):
	#""" This one call the wall to retain the comments of the users in the same entity"""
    def get(self):
        wall_name = self.request.get('wall_name', DEFAULT_WALL)
        if wall_name == DEFAULT_WALL.lower(): wall_name = DEFAULT_WALL
        comments_query = CommentContainer.query(ancestor = wall_key(wall_name)).order(-CommentContainer.date)
        self.render("content.html", comments = comments_query)


class Post(Handler):
	"""This class deals with the users that make a comment 
	or didn't comment at all, if that's the case it will send 
	them to another page with a button telling them to return 
	to the comment section"""
	def post(self):
		wall_name = self.request.get('wall_name',DEFAULT_WALL)
		comment_container = CommentContainer(parent = wall_key(wall_name))
		comment_container.name = self.request.get('name')
		comment_container.content = self.request.get('content')
		if comment_container.content == '':
			self.redirect("/error")
		elif comment_container.content.isspace():
			self.redirect("/error")
		else:
			comment_container.put()
			self.redirect('/#comment_section')

			
			
class Error_Page(Handler):
	"""This controls empty comments"""
	def get(self):
		self.render("error.html")
		

app = webapp2.WSGIApplication([
								("/", MainPage),
								("/comments", Post),
								("/error", Error_Page)
								],
								debug = True)

