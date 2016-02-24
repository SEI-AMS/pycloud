# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

import logging

from pylons import request
from pylons import response, session, tmpl_context as c

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import InstancesPage
from pycloud.pycloud.model import Service, ServiceVM, PairedDevice
from pycloud.pycloud.pylons.lib.util import asjson

from pycloud.pycloud.utils import ajaxutils
from pycloud.pycloud.network import wifi, finder
from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.model import migrator

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs Instances page.
################################################################################################################
class InstancesController(BaseController):

    ############################################################################################################
    # Shows the list of running Service VM instances.
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.servicevms_active = 'active'
        svms = ServiceVM.find()

        # Setup the page to render.
        instancesPage = InstancesPage()
        instancesPage.svms = svms

        # Get the current connection.
        wifi_manager = wifi.WifiManager()
        wifi_manager.interface = 'wlan0'
        instancesPage.current_network = wifi_manager.current_network()

        # Get a list of paired cloudlet networks in range.
        available_networks = wifi_manager.list_networks()
        paired_networks = PairedDevice.by_type('cloudlet')
        paired_networks_in_range = {}
        for paired_network in paired_networks:
            if paired_network.connection_id in available_networks:
                paired_networks_in_range[paired_network.connection_id] = paired_network.connection_id

        # Filter out ourselves.
        current_network = wifi_manager.current_network()
        if current_network in paired_networks_in_range:
            del paired_networks_in_range[current_network]

        instancesPage.available_networks = paired_networks_in_range
        instancesPage.network = current_network

        # Get a list of cloudlets in our current networks.
        cloudlet_finder = finder.CloudletFinder()
        cloudlets = cloudlet_finder.find_cloudlets()

        # Filter out ourselves from the list of cloudlets.
        current_cloudlet = Cloudlet.get_hostname()
        if current_cloudlet in cloudlets:
            cloudlets.remove(current_cloudlet)

        # Show only paired cloudlets.
        paired_cloudlets = {}
        paired_networks = PairedDevice.by_type('cloudlet')
        for paired_cloudlet in paired_networks:
            if paired_cloudlet.device_id in cloudlets:
                host = paired_cloudlet.device_id + ":" + str(cloudlets[paired_cloudlet.device_id].port)
                paired_cloudlets[host] = host
        instancesPage.available_cloudlets = paired_cloudlets
        print 'Paired and available cloudlets: '
        print instancesPage.available_cloudlets

        # Pass the grid and render the page.
        return instancesPage.render()

    ############################################################################################################
    # Starts a new SVM instance of the Service.
    ############################################################################################################
    @asjson
    def GET_startInstance(self, id):
        # Look for the service with this id
        service = Service.by_id(id)
        if service:
            clone_full_image = False
            if request.params.get('clone_full_image'):
                clone_full_image = True

            # Get a ServiceVM instance
            svm = service.get_vm_instance(clone_full_image=clone_full_image)
            try:
                # Start the instance, if it works, save it and return ok
                svm.start()
                svm.save()
                return svm
            except Exception as e:
                # If there was a problem starting the instance, return that there was an error.
                msg = 'Error starting Service VM Instance: ' + str(e)
                return ajaxutils.show_and_return_error_dict(msg)
        else:
            msg = 'Service {} not found.'.format(id)
            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    # Stops an existing instance.
    ############################################################################################################
    @asjson
    def GET_stopInstance(self, id):
        try:    
            # Stop an existing instance with the given ID.
            svm = ServiceVM.find_and_remove(id)
            svm.destroy()
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            msg = 'Error stopping Service VM Instance: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

        # Everything went well.
        return ajaxutils.JSON_OK

    ############################################################################################################
    # Command to migrate a machine.
    ############################################################################################################
    @asjson
    def GET_migrateInstance(self, id):
        try:
            remote_host = request.params.get('target', None)
            migrator.migrate_svm(id, remote_host)
        except Exception, e:
            msg = 'Error migrating: ' + str(e)
            import traceback
            traceback.print_exc()

            return ajaxutils.show_and_return_error_dict(msg)

        return ajaxutils.JSON_OK

    ############################################################################################################
    # Returns a list of running svms.
    ############################################################################################################    
    @asjson    
    def GET_svmList(self):
        try:    
            # Get the list of running instances.
            svm_list = ServiceVM.find()
            return svm_list
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            msg = 'Error getting list of instance changes: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    # Returns a list of running svms.
    ############################################################################################################
    @asjson
    def GET_wifiConnect(self):
        ssid = request.params.get('target')
        wifi_manager = wifi.WifiManager()
        wifi_manager.interface = 'wlan0'

        try:
            result = wifi_manager.connect_to_network(ssid)
        except Exception as e:
            msg = 'Error connecting to Wi-Fi network {}: {}'.format(ssid, str(e))
            return ajaxutils.show_and_return_error_dict(msg)

        if result:
            return ajaxutils.JSON_OK
        else:
            return ajaxutils.show_and_return_error_dict('Could not connect to Wi-Fi network {}'.format(ssid))
