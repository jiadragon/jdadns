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
		#logging.info('DNS called from '+obj_name+' owned by '+owner_name+' ('+owner_key+') from Region:'+region+' Pos:'+local_pos)
		#logging.info('POST Body was: '+self.request.body)

    admin_password = "adminpassword"        # This password enables you to have unrestricted access to the DNS
    # Putting "null" in password disables this feature.
 
    if self.request.get('type')=='add':    # Adding a new service to the DNS (You can also use Update but it won't tell you the service already exists)
      param2=self.request.get('name')   # the Name the service will be known by
      param3=self.request.get('url')    # the URL for the web service
      param4=self.request.get('wpass')  # the password for modifying the entry
      param5=self.request.get('rpass')  # the password for reading the entry
      param6=self.request.get('hidden') # enables hiding the entry from listing
 
      if admin_password != 'null' and admin_password == self.request.get('admin'):
        newrec = Service.get_by_key_name(param2)
    elif self.request.get('type')=='list': # List the existing services
      records = Service.all()
      if records is None:
        logging.info('Service List: Empty')
        self.response.out.write('Empty') # Services weren't found
      else:
        got_admin = False
        if admin_password != 'null' and admin_password == self.request.get('admin'):
        got_admin = True;            
        for result in records: 
          if result.hidden == False or got_admin == True:
                self.response.out.write(result.name+',')
            logging.info('Service List: Success')
            self.response.out.write('END')  # Cap the list             
 
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
