import logging

# Pylon imports.
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from paste import fileapp

# For serializing JSON data.
import json

# To get our IP.
import urlparse

# To handle basic OS stuff.
import os

# Controller to derive from.
from pycloud.manager.lib.base import BaseController

from pycloud.pycloud.utils import timelog

log = logging.getLogger(__name__)

################################################################################################################
# Class that handles Service VM related HTTP requests to a Cloudlet.
################################################################################################################
class AppPushController(BaseController):
    
    # Folder where apps to be pushed are stored.
    APPS_FOLDER = os.path.join(os.path.abspath(os.getcwd()), "data/app_rep/")  

    ################################################################################################################
    # Called to get a list of apps available at the server.
    ################################################################################################################
    def GET_getList(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request for stored apps received.")
            
        # Create a single json from the json for individual apps. 
        #path = os.path.dirname(os.path.abspath(self.APPS_FOLDER))
        path = os.path.abspath(self.APPS_FOLDER)
        print path
        
        apps = []
        for root, dirs, files in os.walk(path):  # @UnusedVariable
            # Loop over all subfolders, one for each app.
            for subdirname in dirs:
                subdirpath = os.path.join(path,subdirname)
                for r, d, f in os.walk(subdirpath):  # @UnusedVariable
                    # Loop over all files in that subfolder to find a JSON one.
                    for filename in f:
                        if filename.endswith(".json"):
                            # Construct the full path for the json file.
                            jsonfile = os.path.join(r, filename)
                            jsonfile = os.path.join(root, jsonfile)
                            print jsonfile
                            
                            # Open the json file and add the contents to the array of json contents. 
                            json_data = open(jsonfile)
                            apps.append(json.load(json_data))
    
        # Create a JSON response that includes all the json content from all metadata files.
        jsonDataStructure = { 'apps' : apps }
        jsonDataString = json.dumps(jsonDataStructure, indent=2)
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        responseText = jsonDataString
        return responseText       
        
    ################################################################################################################
    # Called to get an app from the server.
    ################################################################################################################
    def GET_getApp(self):

        appName = request.GET['appName']
        print '\n*************************************************************************************************'    
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request to push app received.")
        
        # Find a folder with a name matching the app and return the .apk inside.
        app_file_path = ''
        print "Got app name " + appName 
        path = os.path.dirname(os.path.abspath(self.APPS_FOLDER))
        for root, dirs, files in os.walk(path):  # @UnusedVariable
            # Loop over all subfolders, to find the one for this app.
            for subdirname in dirs:
                if subdirname == appName:
                    # We found the folder for this app.
                    print "appname matches subdir " + appName + " " + subdirname 
                    for r, d, f in os.walk(os.path.join(root,subdirname)):  # @UnusedVariable
                        # Loop over all the files in the folder to find the .apk
                        for filename in f: 
                            print filename 
                            if filename.endswith(".apk"):
                                # Construct the full file path to the apk file.
                                apkfile = os.path.join(r, filename)
                                apkfile = os.path.join(root, apkfile) 
                                app_file_path = apkfile 
                                print "returning " + app_file_path
                                
                                # We don't need to continue searching, we have our apk.
                                break
        
        # Send the response, serving the apk file back to the client.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        fapp = fileapp.FileApp(app_file_path, content_disposition='attachment; filename="'+filename+'"')
        return fapp(request.environ, self.start_response)        
#        return cherrypy.lib.static.serve_file(app_file_path, "application/x-download", "attachment") 