import logging, urllib
 
import webapp2
from google.appengine.ext import db
 
class Service(db.Model):
  name = db.StringProperty(multiline=False)
  url = db.StringProperty(multiline=False,indexed=False)
  writepass = db.StringProperty(multiline=False,indexed=False)
  readpass = db.StringProperty(multiline = False,indexed=False)
  hidden = db.BooleanProperty(indexed=False)
 
class Main_DNS(webapp2.RequestHandler):
 
  def get(self):
 
    self.response.out.write('None') # Service wasn't found
    obj_name=self.request.headers.get('X-SecondLife-Object-Name')
    region=self.request.headers.get('X-SecondLife-Region')
    local_pos=self.request.headers.get('X-SecondLife-Local-Position')
    owner_name=self.request.headers.get('X-SecondLife-Owner-Name')
    owner_key=self.request.headers.get('X-SecondLife-Owner-Key')
		logging.info('DNS called from '+obj_name+' owned by '+owner_name+' ('+owner_key+') from Region:'+region+' Pos:'+local_pos)
		logging.info('POST Body was: '+self.request.body)
 


  def post(self):
   self.get()
 
class Redirector(webapp2.RequestHandler):
  def get(self):
 
    import urllib
 
    service_name=self.request.path
 
    if service_name[-1]=='/' :
      service_name=service_name[1:-1] #remove leading and trailing slash
    else:
      service_name=service_name[1:]  # remove leading slash only
 
    #un-escape just in case you're Kinki :p
    service_name=urllib.unquote(service_name)
    logging.debug('Looking up '+service_name+' (DNS)');
 
    record = Service.get_by_key_name(str(service_name))
 
    if record is None:
        logging.info('Redirect Failed: Not Found')   
        self.response.out.write('None') # Service wasn't found
    elif record.readpass != '':
        self.response.set_status(403)
        logging.info('Redirect Failed: Read Protected. Use "retrieve" command type to get URL.') 
        self.response.out.write("<html><title>403 Forbidden</title><body>Cannot forward a read-protected entry.</body></html>")
    else:
        logging.info('Redirect Success') 
        if self.request.query_string != '' :
            self.redirect(urllib.unquote(record.url)+'/?'+self.request.query_string) # redirect to the HTTP-IN URL with arugments
        else:        
            self.redirect(urllib.unquote(record.url)) # redirect to the HTTP-IN URL    
 
app = webapp2.WSGIApplication( [('/', Main_DNS),
                                ('/.*',Redirector)], 
                                 debug=True)
