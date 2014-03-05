#!/usr/bin/env python
#       

# For file handling.
import os.path

# To delete folder contents and to move files.
import shutil

# For configuration file management.
from pycloud.pycloud.utils. import config

# To handle the actual VMs (from this same package).
import instance

# To handle ports.
from pycloud.pycloud.utils import portmanager

################################################################################################################
# Exception type used in our system.
################################################################################################################
class ServiceVMInstanceManagerException(Exception):
    def __init__(self, message):
        super(ServiceVMInstanceManagerException, self).__init__(message)
        self.message = message   

################################################################################################################
# Handles ServerVM Instances.
################################################################################################################
class ServiceVMInstanceManager(object):

    # Name of the configuration section for this class's parameters.    
    CONFIG_SECTION = 'servicevm'
    
    # Param name for configuration of root folder where transient VMs are executed.
    INSTANCES_FOLDER_KEY = 'service_vm_instances_folder'  
    
    # Map of running VM instances, keyed by instance id.
    serviceVMInstances = {}

    # Map of list of running VM instances, stored by service id.
    runningServices = {}

    ################################################################################################################  
    # Method to simply getting configuration values for this module.
    ################################################################################################################       
    def __getLocalConfigParam(self, key):
        return config.Configuration.getParam(self.CONFIG_SECTION, key)

    ################################################################################################################  
    # Cleans up the root folder for VMs instances.
    ################################################################################################################   
    def cleanupInstancesFolder(self):
        rootInstancesFolder = self.__getLocalConfigParam(self.INSTANCES_FOLDER_KEY)
        if(os.path.exists(rootInstancesFolder)):
            shutil.rmtree(rootInstancesFolder)
        if(not os.path.exists(rootInstancesFolder)):
            os.makedirs(rootInstancesFolder)  

    ################################################################################################################  
    # Constructor.
    ################################################################################################################       
    def __init__(self):
        # Cleanup the VMs instances folder.
        self.cleanupInstancesFolder()
        portmanager.PortManager.clearPorts()
        
    ################################################################################################################  
    # Starts an instance of a Service VM, or joins an existing one.
    ################################################################################################################   
    def getServiceVMInstance(self, serviceId, serverHostPort=None, showVNC=False, joinExisting=False):
        # By default we don't have a running instance.
        runningInstance = None
                
        # If we are allowed to use an existing instance for this service, check if there is one running.
        if(joinExisting):
            # Check if there are instances associated with the given service id.
            if((serviceId in self.runningServices) and (len(self.runningServices[serviceId]) > 0)):
                # Check the list of instances associated with this service.
                serviceIdInstances = self.runningServices[serviceId]
                print 'Running instances for service %s: %d.' % (serviceId,len(serviceIdInstances))
                for instanceId in serviceIdInstances:
                    # We will just pick the first one to use (bad load balancing...).
                    runningInstance = serviceIdInstances[instanceId]
                    break;
            
        # Check if we have to start a new transient VM.
        newInstanceNeeded = runningInstance == None
        if(newInstanceNeeded):
            runningInstance = self.__createNewInstance(serviceId, serverHostPort, showVNC)
        
        # Return the instance information.
        return runningInstance
    
    ################################################################################################################  
    # Creates a new Server VM instance, and records all pertinent information in memory so we can track it.
    ################################################################################################################  
    def __createNewInstance(self, serviceId, serviceHostPort, showVNC):
        # If no host port was provided, look for a free one.
        # This could still choose a port in use by another process.
        if(serviceHostPort == None):
            serviceHostPort = portmanager.PortManager.generateRandomAvailablePort()
            
        # Look for a free port for SSH.
        # This could still pick a port in use by another process.
        sshHostPort = portmanager.PortManager.generateRandomAvailablePort()
        
        # Start a new transient VM.
        instancesRootFolder = self.__getLocalConfigParam(self.INSTANCES_FOLDER_KEY)
        serviceVMInstance = instance.ServiceVMInstance(serviceId, serviceHostPort, sshHostPort, instancesRootFolder)
        serviceVMInstance.createAndStart(showVNC)
    
        # Save this instance in our list of running instances.
        print "Adding to running instances list " + serviceVMInstance.instanceId
        self.serviceVMInstances[serviceVMInstance.instanceId] = serviceVMInstance
        
        # We also store these instances by Service Id, so we can easily check if a certain service has a running instance without
        # going through the whole list.
        if(not self.runningServices.has_key(serviceId)):
            self.runningServices[serviceId] = {}
        self.runningServices[serviceId][serviceVMInstance.instanceId] = serviceVMInstance
        
        return serviceVMInstance        
                            
    ################################################################################################################  
    # Stops a running instance of a Service VM.
    ################################################################################################################   
    def stopServiceVMInstance(self, instanceId):
        try:
            # Get the instance.
            serviceVMInstance = self.serviceVMInstances.pop(instanceId, None)
            
            # Check if this instance is actually running according to our records.
            if(serviceVMInstance == None):
                print('Warning: attempting to stop VM that is not registered in list of running VMs: ' + instanceId)            
            
            # Stop the VM instance.
            serviceVMInstance.stop()
        except instance.ServiceVMException as exception:
            # Most likely VM could not be found.
            print 'Error stopping VM instance with id ' + instanceId + ': ' + str(exception)
            raise ServiceVMInstanceManagerException('Error stopping VM instance: ' + exception.message)
        finally:            
            if(serviceVMInstance != None):
                print "Cleaning up VM instance data."
                                
                # Release the ports.
                portmanager.PortManager.freePort(serviceVMInstance.serviceHostPort)      
                portmanager.PortManager.freePort(serviceVMInstance.sshHostPort)
            
                # Remove this from our list of running instances for a particular Service id.
                serviceId = serviceVMInstance.serviceId
                if(self.runningServices.has_key(serviceId)):
                    self.runningServices[serviceId].pop(instanceId, None)
                else:                
                    print "Server id entry not found while cleaning up VM instance."
                    
    ################################################################################################################  
    # Returns the running Service VM instances.
    ################################################################################################################    
    def getServiceVMInstances(self):
        return serviceVMInstances
                    
    ################################################################################################################  
    # Stops all existing running vms.
    ################################################################################################################              
    def cleanup(self):
        # Loop over all running vms.
        for instanceId in self.serviceVMInstances.keys():
            self.stopServiceVMInstance(instanceId)       
            
        # Clear any stored ports, if any.
        portmanager.PortManager.clearPorts()