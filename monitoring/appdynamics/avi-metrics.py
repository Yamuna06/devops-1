#!/usr/bin/python


version = 'v2017-12-04'

#########################################################################################
#                                                                                       #
#                                                                                       #
#                                                                                       #
#  REQUIREMENTS:                                                                        #
#    1. python 2.7                                                                      #
#    2. python requests                                                                 #
#                                                                                       #
#                                                                                       #
#                                                                                       #
#                                                                                       #
#  @author: Matthew Karnowski (mkarnowski@avinetworks.com)                              #
#                                                                                       #
#                                                                                       #
#                                                                                       #
#########################################################################################
#########################################################################################

#----- Import Libraries

import requests
import json
import time
import syslog
import socket
from multiprocessing import Process
from datetime import datetime
import base64
import logging
import traceback
import argparse
import sys
import os





#----- Logging Information
logging_enabled = True   #---True/False
enable_debug = True   #---True/False, default logging is ERROR
fdir = os.path.abspath(os.path.dirname(__file__))
log_file = fdir+'/avi_metrics.log'






#----- Send value to appdynamics
def send_value_appdynamics(name, value, timestamp):
    print('name=Custom Metrics|%s,value=%d,aggregator=OBSERVATION,time-rollup=CURRENT,cluster-rollup=INDIVIDUAL' % (name.replace('.','|'), long(value)))



#----- This function is used to loop through a list of Classes and send to
#----- appdynamics.
#-----    1.  name_space
#-----    2.  value
#-----    3.  timestamp
def send_class_list_appdynamics(class_list):
    for entry in class_list:
        print('name=Custom Metrics|%s,value=%d,aggregator=OBSERVATION,time-rollup=CURRENT,cluster-rollup=INDIVIDUAL' % (entry.name_space.replace('.','|'), long(entry.value)))




#----- This function allows for passwords to be either plaintext or base64 encoded
def isBase64(password):
    try:
        if base64.b64encode(base64.b64decode(password)) == password:
            return base64.b64decode(password)
        else:
            return password
    except Exception:
        return password




#----- This class is where all the test methods/functions exist and are executed
class avi_metrics():
    def __init__(self,avi_controller,host_location,host_environment, avi_user, avi_pass):
        self.avi_controller = avi_controller
        self.host_location = host_location
        self.host_environment = host_environment
        self.avi_user = avi_user
        self.avi_pass = avi_pass
        vs_metric_list  = [
            'l4_server.avg_errored_connections',
            'l4_server.avg_rx_pkts',
            'l4_server.avg_bandwidth',
            'l4_server.avg_server_count',
            'l4_server.avg_open_conns',
            'l4_server.avg_new_established_conns',
            'l4_server.avg_pool_complete_conns',
            'l4_server.sum_num_state_changes',
            'l4_server.sum_rx_zero_window_size_events',
            'l4_server.sum_tx_zero_window_size_events',
            'l4_server.sum_out_of_orders',
            'l4_server.sum_sack_retransmits',
            'l4_server.sum_timeout_retransmits',
            'l4_server.apdexc',
            'l4_server.avg_total_rtt',
            'l4_client.apdexc',
            'l4_client.avg_bandwidth',
            'l4_client.avg_application_dos_attacks',
            'l4_client.avg_complete_conns',
            'l4_client.avg_connections_dropped',
            'l4_client.avg_new_established_conns',
            'l4_client.avg_policy_drops',
            'l4_client.avg_rx_pkts',
            'l4_client.avg_tx_pkts',
            'l4_client.avg_rx_bytes',
            'l4_client.avg_tx_bytes',
            'l4_client.avg_rx_pkts_dropped',
            'l4_client.sum_packet_dropped_user_bandwidth_limit',
            'l4_client.max_open_conns',
            'l7_client.avg_complete_responses',
            'l7_client.avg_client_data_transfer_time',
            'l7_client.avg_resp_4xx_avi_errors',
            'l7_client.avg_resp_5xx_avi_errors',
            'l4_client.avg_total_rtt',
            'l7_client.avg_resp_4xx',
            'l7_client.avg_resp_5xx',
            'l7_server.avg_resp_4xx',
            'l7_server.avg_resp_5xx',
            'l7_server.avg_resp_latency',
            'l7_server.apdexr',
            'l7_client.avg_page_load_time',
            'l7_client.apdexr',
            'l7_client.avg_ssl_handshakes_new',
            'l7_client.avg_ssl_connections',
            'l7_server.avg_application_response_time',
            'l7_server.pct_response_errors',
            'l7_server.avg_frustrated_responses',
            'l7_client.avg_frustrated_responses',
            'l7_client.avg_waf_attacks',
            'l7_client.pct_waf_attacks',
            'dns_client.avg_complete_queries',
            'dns_client.avg_domain_lookup_failures',
            'dns_client.avg_tcp_queries',
            'dns_client.avg_udp_queries',
            'dns_client.avg_udp_passthrough_resp_time',
            'dns_client.avg_unsupported_queries',
            'dns_client.pct_errored_queries',
            'dns_client.avg_domain_lookup_failures',
            'dns_client.avg_avi_errors',
            'dns_server.avg_complete_queries',
            'dns_server.avg_errored_queries',
            'dns_server.avg_tcp_queries',
            'dns_server.avg_udp_queries']
        self.vs_metric_list = ','.join(vs_metric_list)
        se_metric_list = [
            'se_stats.avg_bandwidth', #--- pre 17.x
            'se_if.avg_bandwidth', #--- post 17.x
            'se_stats.avg_connection_mem_usage',
            'se_stats.avg_connection_policy_drops',
            'se_stats.avg_connections',
            'se_stats.avg_connections_dropped',
            'se_stats.avg_cpu_usage',
            'se_stats.avg_disk1_usage',
            'se_stats.avg_mem_usage',
            'se_stats.avg_persistent_table_size',
            'se_stats.avg_persistent_table_usage',
            'se_stats.avg_rx_bandwidth',
            'se_if.avg_rx_bytes',  #--- post 17.x
            'se_stats.avg_rx_pkts', #--- pre 17.x
            'se_if.avg_rx_pkts', #--- post 17.x
            'se_stats.avg_rx_pkts_dropped', #--- pre 17.x
            'se_if.avg_rx_pkts_dropped_non_vs', #--- post 17.x
            'se_stats.avg_tx_pkts', #--- pre 17.x
            'se_if.avg_tx_pkts', #--- post 17.x
            'se_if.avg_tx_bytes',  #--- post 17.x
            'se_stats.avg_ssl_session_cache_usage',
            'se_stats.max_connection_mem_total',
            'se_stats.max_connection_table_size',
            'se_if.avg_connection_table_usage', #--- post 17.x
            'se_stats.avg_ssl_session_cache',
            'se_stats.max_num_vs',
            'se_stats.max_se_bandwidth',
            'se_stats.sum_connection_dropped_memory_limit',
            'se_stats.sum_connection_dropped_packet_buffer_stressed',
            'se_stats.sum_connection_dropped_persistence_table_limit',
            'se_stats.sum_packet_buffer_allocation_failure',
            'se_stats.sum_packet_dropped_packet_buffer_stressed',
            'se_stats.sum_cache_object_allocation_failure',
            'se_stats.avg_eth0_rx_pkts',
            'se_stats.avg_eth0_tx_pkts',
            'se_stats.avg_eth0_bandwidth',
            'se_stats.pct_syn_cache_usage',
            'se_stats.avg_packet_buffer_usage',
            'se_stats.avg_packet_buffer_header_usage',
            'se_stats.avg_packet_buffer_large_usage',
            'se_stats.avg_packet_buffer_small_usage']
        #----
        self.se_metric_list = ','.join(se_metric_list)


    def avi_login(self):
        login = requests.post('https://%s/login' %self.avi_controller, verify=False, data={'username': self.avi_user, 'password': self.avi_pass},timeout=15)
        return login


    def avi_request(self,avi_api,tenant):
        headers = ({"X-Avi-Tenant": "%s" %tenant, 'content-type': 'application/json'})
        return requests.get('https://%s/api/%s' %(self.avi_controller,avi_api), verify=False, headers = headers,cookies=dict(sessionid= self.login.cookies['sessionid']),timeout=50)


    def avi_post(self,api_url,tenant,payload):
        headers = ({"X-Avi-Tenant": "%s" %tenant, 'content-type': 'application/json','referer': 'https://%s' %self.avi_controller, 'X-CSRFToken': dict(self.login.cookies)['csrftoken']})
        cookies = dict(sessionid= self.login.cookies['sessionid'],csrftoken=self.login.cookies['csrftoken'])
        return requests.post('https://%s/api/%s' %(self.avi_controller,api_url), verify=False, headers = headers,cookies=cookies, data=json.dumps(payload),timeout=50)



    #-----------------------------------
    #----- Add Test functions
    #-----------------------------------
    def srvc_engn_vs_count(self):
        try:
            temp_start_time = time.time()
            discovered_vs = []  #--- this is used b/c vs in admin show up in other tenants
            srvc_engn_dict = {}
            for t in self.tenants:
                srvc_engn_list = self.avi_request('serviceengine?page_size=1000',t['name']).json()['results']
                for entry in srvc_engn_list:
                    if 'consumers' in entry.keys():
                        for v in entry['consumers']:
                            if entry['name']+v['con_uuid'] not in discovered_vs:
                                discovered_vs.append(entry['name']+v['con_uuid'])
                                if entry['name'] not in srvc_engn_dict:
                                    srvc_engn_dict[entry['name']] = 1
                                else:
                                    srvc_engn_dict[entry['name']] +=1
                    elif 'vs_uuids' in entry.keys(): #---- 17.2.4 api changed
                        for v in entry['vs_uuids']:
                            if entry['name']+v.rsplit('api/virtualservice/')[1] not in discovered_vs:
                                discovered_vs.append(entry['name']+v.rsplit('api/virtualservice/')[1])
                                if entry['name'] not in srvc_engn_dict:
                                    srvc_engn_dict[entry['name']] = 1
                                else:
                                    srvc_engn_dict[entry['name']] +=1
                    else:
                        if entry['name'] not in srvc_engn_dict:
                            srvc_engn_dict[entry['name']] = 0
            if len(srvc_engn_dict) > 0:
                for entry in srvc_engn_dict:
                    send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.vs_count' %entry.replace('.','_'), srvc_engn_dict[entry], int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func srvc_engn_vs_count completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func srvc_engn_vs_count encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)

    #-----------------------------------

    def srvc_engn_count(self):
        try:
            temp_start_time = time.time()
            discovered_ses = []  #--- this is used b/c se in admin show up in other tenants
            se_count = 0
            for t in self.tenants:
                resp = self.avi_request('serviceengine?page_size=1000',t['name']).json()
                if resp['count'] != 0:
                    for s in resp['results']:
                        if s['name'] not in discovered_ses:
                            se_count +=1
                            discovered_ses.append(s['name'])
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.serviceengine.count',se_count, int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func srvc_engn_count completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func srvc_engn_count encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    #-----------------------------------

    def srvc_engn_stats(self):
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            discovered_ses = []  #--- this is used b/c se in admin show up in other tenants
            discovered_health = []
            se_dict = {}
            for t in self.tenants:
                srvc_engn_list = self.avi_request('serviceengine?page_size=1000',t['name']).json()
                if srvc_engn_list['count'] != 0:
                    for s in srvc_engn_list['results']:
                        se_dict[s['uuid']] = s['name']
                    payload = {
                        "metric_requests": [
                            {
                                "step": 300,
                                "limit": 1,
                                "aggregate_entity": False,
                                "entity_uuid": "*",
                                "se_uuid": "*",
                                "id": "collItemRequest:AllSEs",
                                "metric_id": self.se_metric_list
                            }
                            ]}
                    se_stat = self.avi_post('analytics/metrics/collection?pad_missing_data=false', t['name'], payload).json()
                    payload = {
                        "metric_requests": [
                            {
                                "step": 60,
                                "limit": 1,
                                "aggregate_entity": False,
                                "entity_uuid": "*",
                                "se_uuid": "*",
                                "id": "collItemRequest:AllSEs",
                                "metric_id": self.se_metric_list
                            }
                            ]}
                    realtime_stat = self.avi_post('analytics/metrics/collection?pad_missing_data=false', t['name'], payload).json()
                    se_stat['series']['collItemRequest:AllSEs'].update(realtime_stat['series']['collItemRequest:AllSEs'])
                    for s in se_stat['series']['collItemRequest:AllSEs']:
                        se_name = se_dict[s]
                        if se_name not in discovered_ses:
                            discovered_ses.append(se_name)
                            for entry in se_stat['series']['collItemRequest:AllSEs'][s]:
                                if 'data' in entry:
                                    class appdynamics_class(): pass
                                    metric_name = entry['header']['name'].replace('.','_')
                                    metric_value = entry['data'][0]['value']
                                    x = appdynamics_class
                                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.%s' %(se_name.replace('.','_'), metric_name)
                                    x.value = metric_value
                                    x.timestamp = int(time.time())
                                    appdynamics_class_list.append(x)
                    #----- PULL SERVICE ENGINE HEALTHSCORES
                    avi_api = 'analytics/healthscore/serviceengine?page_size=1000'
                    se_healthscore = self.avi_request(avi_api,t['name']).json()['results']
                    for s in se_healthscore:
                        se_name = se_dict[s['entity_uuid']]
                        if se_name not in discovered_health:
                            discovered_health.append(se_name)
                            class appdynamics_class(): pass
                            health_metric = s['series'][0]['data'][0]['value']
                            x = appdynamics_class
                            x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.healthscore' %se_name.replace('.','_')
                            x.value = health_metric
                            x.timestamp = int(time.time())
                            appdynamics_class_list.append(x)
                    self.se_vnic_portgroup(appdynamics_class_list,t['name']) #---- Run function to look at se portgroup membership
                    self.se_missed_hb(srvc_engn_list,appdynamics_class_list)  #---- Run function to look for missed heartbeats
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func srvc_engn_stats completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func srvc_engn_stats encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)

    #-----------------------------------

    def srvc_engn_dispatcher_cpu_usage(self):
        try:
            temp_start_time = time.time()
            srvc_engn_dict = {}
            appdynamics_class_list = []
            for t in self.tenants:
                srvc_engn_list = self.avi_request('serviceengine?page_size=1000',t['name']).json()['results']
                if len(srvc_engn_list) > 0:
                    for entry in srvc_engn_list:
                        if entry['uuid'] not in srvc_engn_dict:
                            srvc_engn_dict[entry['uuid']] = entry['name']
                            dispatcher_usage = self.avi_request('serviceengine/%s/cpu' %entry['uuid'],t['name']).json()[0]['process_cpu_utilization']
                            if type(dispatcher_usage) == list:
                                for cpu_resp in dispatcher_usage:
                                    if 'dp' in cpu_resp['process_name']:
                                        class appdynamics_class(): pass
                                        metric_name = cpu_resp['process_name'].replace('.','_')
                                        metric_value = cpu_resp['process_cpu_usage']
                                        x = appdynamics_class
                                        x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.dispatcher_usage.%s' %(entry['name'].replace('.','_'), metric_name)
                                        x.value = metric_value
                                        x.timestamp = int(time.time())
                                        appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func srvc_engn_dispatcher_cpu_usage completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func srvc_engn_dispatcher_cpu_usage encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)

    #-----------------------------------

    def se_bgp_peer_state(self):
        try:
            temp_start_time = time.time()
            srvc_engn_list = self.avi_request('serviceengine?page_size=1000','admin').json()['results']
            appdynamics_class_list = []
            for s in srvc_engn_list:
                b = self.avi_request('serviceengine/'+s['uuid']+'/bgp','admin').json()
                if type(b) == list:
                    for entry in b:
                        if 'peers' in entry:
                            se_name = s['name']
                            for p in entry['peers']:
                                peer_ip = p['peer_ip'].replace('.','_')
                                if 'Established' in p['bgp_state']:
                                    peer_state = 100
                                    if len(p['vs_names']) > 0:
                                        for v in p['vs_names']:
                                            class appdynamics_class(): pass
                                            y = appdynamics_class
                                            y.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.advertised_vs.%s.%s' %(se_name.replace('.','_'), v.replace('.','_'), peer_ip)
                                            y.value = 1
                                            y.timestamp = int(time.time())
                                            appdynamics_class_list.append(y)
                                else:
                                    peer_state = 50
                                class appdynamics_class(): pass
                                x = appdynamics_class
                                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.bgp-peer.%s' %(se_name.replace('.','_'), peer_ip)
                                x.value = peer_state
                                x.timestamp = int(time.time())
                                appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': se_bgp_peer_state, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': se_bgp_peer_state encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)



    #-----------------------------------
    #--- This function will loop through all tenants pulling the following statistics
    #--- for all Virtual Services.
    def virtual_service_stats_threaded(self):
        proc = []
        for t in self.tenants:
            t_name = t['name']
            p = Process(target = self.virtual_service_stats, args = (t_name,))
            p.start()
            proc.append(p)
        for p in proc:
            p.join()




    def virtual_service_stats(self,tenant):
        try:
            temp_start_time = time.time()
            #-----
            virtual_services = self.avi_request('virtualservice?page_size=1000',tenant).json()
            if virtual_services['count'] !=0:
                appdynamics_class_list = []
                vs_dict= {}
                for v in virtual_services['results']:
                    vs_uuid = v['uuid']
                    vs_name = v['name']
                    vs_dict[vs_uuid] = vs_name
                payload =  {'metric_requests': [{'step' : 300, 'limit': 1, 'id': 'allvs', 'entity_uuid' : '*', 'metric_id': self.vs_metric_list}]}
                vs_stats = self.avi_post('analytics/metrics/collection?pad_missing_data=false', tenant, payload).json()
                #----- this pulls 1 min avg stats for vs that have realtime stats enabled
                payload =  {'metric_requests': [{'step' : 60, 'limit': 1, 'id': 'allvs', 'entity_uuid' : '*', 'metric_id': self.vs_metric_list}]}
                realtime_stats = self.avi_post('analytics/metrics/collection?pad_missing_data=false', tenant, payload).json()
                #----- overwrites real time vs' 5 min avg with the 1 min avg
                vs_stats['series']['allvs'].update(realtime_stats['series']['allvs'])
                #----- THIS IS NEW
                for v in vs_stats['series']['allvs']:
                    if v in vs_dict:
                        vs_uuid = v
                        vs_name = vs_dict[vs_uuid].replace('.','_')
                        for m in vs_stats['series']['allvs'][v]:
                            class appdynamics_class(): pass #----- class will be used to create a list for optimized graphite metric sending
                            metric_name = m['header']['name'].replace('.','_')
                            if 'data' in m:
                                metric_value = m['data'][0]['value']
                                x = appdynamics_class
                                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.%s' %(vs_name, metric_name)
                                x.value = metric_value
                                x.timestamp = int(time.time())
                                appdynamics_class_list.append(x)
                send_class_list_appdynamics(appdynamics_class_list)
            #-----------------------------------
            #----- SEND SUM OF VS_COUNT LIST - TOTAL NUMBER OF VS
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func virtual_service_stats completed for tenant: '+tenant+', executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func virtual_service_stats encountered an error for tenant'+tenant)
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)



    def vs_metrics_per_se_threaded(self):
        try:
            temp_start_time = time.time()
            vs_dict= {}
            proc = []
            admin_vs = []
            for t in self.tenants:
                virtual_services = self.avi_request('virtualservice?page_size=1000',t['name']).json()
                if virtual_services['count'] !=0:
                    for v in virtual_services['results']:
                        vs_uuid = v['uuid']
                        vs_name = v['name']
                        vs_dict[vs_uuid] = vs_name
                        if t['name'] == 'admin':
                            admin_vs.append(vs_uuid)
            if len(vs_dict) > 0:
                for t in self.tenants:
                    srvc_engn_list = self.avi_request('serviceengine?page_size=1000',t['name']).json()
                    if srvc_engn_list['count'] != 0:
                        se_dict = {}
                        for s in srvc_engn_list['results']:
                            se_dict[s['uuid']] = s['name']
                        for se in se_dict:
                            p = Process(target = self.vs_metrics_per_se, args = (se_dict,vs_dict,se,t['name'],admin_vs,))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vs_metrics_per_se_threaded completed, executed in '+temp_total_time+' seconds')
        except:
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    def vs_metrics_per_se(self,se_dict,vs_dict,se,tenant,admin_vs):
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            payload =  {'metric_requests': [{'step' : 300, 'limit': 1, 'id': 'vs_metrics_by_se', 'entity_uuid' : '*', 'serviceengine_uuid': se, 'include_refs': True, 'metric_id': self.vs_metric_list}]}
            vs_stats = self.avi_post('analytics/metrics/collection?pad_missing_data=false', tenant, payload).json()
            #----- this will pull 1 min stats for vs that have realtime stat enabled
            payload =  {'metric_requests': [{'step' : 60, 'limit': 1, 'id': 'vs_metrics_by_se', 'entity_uuid' : '*', 'serviceengine_uuid': se, 'include_refs': True, 'metric_id': self.vs_metric_list}]}
            realtime_stats = self.avi_post('analytics/metrics/collection?pad_missing_data=false', tenant, payload).json()
            #----- overwrite 5 min avg stats with 1 min avg stats for vs that have realtime stats enabled
            vs_stats['series']['vs_metrics_by_se'].update(realtime_stats['series']['vs_metrics_by_se'])
            if len(vs_stats['series']['vs_metrics_by_se']) > 0:
                for entry in vs_stats['series']['vs_metrics_by_se']:
                    if tenant == 'admin' and entry not in admin_vs:
                        continue
                    elif tenant != 'admin' and entry in admin_vs:
                        continue
                    else:
                        vs_name = vs_dict[entry].replace('.','_')
                        for d in vs_stats['series']['vs_metrics_by_se'][entry]:
                            if 'data' in d:
                                class appdynamics_class(): pass
                                metric_name = d['header']['name'].replace('.','_')
                                metric_value = d['data'][0]['value']
                                x = appdynamics_class
                                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.virtualservice_stats.%s.%s' %(se_dict[se].replace('.','_'),vs_name,metric_name)
                                x.value = metric_value
                                x.timestamp = int(time.time())
                                appdynamics_class_list.append(x)
                if len(appdynamics_class_list) > 0:
                    send_class_list_appdynamics(appdynamics_class_list)
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func vs_metrics_per_se completed for se '+se_dict[se]+' tenant: '+tenant+', executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vs_metrics_per_se for se '+se_dict[se]+' tenant: '+tenant+', encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)








    #----- PULL VS HEALTHSCORES
    def vs_healthscores(self):
        #----- PULL VS HEALTHSCORES
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            vs_dict = {}
            for t in self.tenants:
                virtual_services = self.avi_request('virtualservice-inventory?page_size=1000&include=health_score',t['name']).json()['results']
                for v in virtual_services:
                    vs_name = v['config']['name'].replace('.','_')
                    vs_healthscore = v['health_score']['health_score']
                    class appdynamics_class(): pass #----- class will be used to create a list for optimized graphite metric sending
                    x = appdynamics_class
                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.healthscore' %vs_name
                    x.value = vs_healthscore
                    x.timestamp = int(time.time())
                    appdynamics_class_list.append(x)
            send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vs_healthscores completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vs_healthscores encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    def vs_oper_status(self):
        #----- PULL VS UP/DOWN STATUS
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            vs_up_count = 0
            vs_down_count = 0
            vs_disabled_count = 0
            vs_count = 0
            for t in self.tenants:
                virtual_service_status = self.avi_request('virtualservice-inventory?page_size=1000',t['name']).json()['results']
                vs_count += len(virtual_service_status)
                for v in virtual_service_status:
                    class appdynamics_class(): pass
                    vs_name = v['config']['name'].replace('.','_')
                    metric_name = 'oper_status'
                    if v['runtime']['oper_status']['state'] == 'OPER_UP':
                        metric_value = 1
                        vs_up_count += 1
                    elif v['runtime']['oper_status']['state'] == 'OPER_DISABLED':
                        metric_value = 0
                        vs_down_count += 1
                        vs_disabled_count += 1
                    else:
                        metric_value = 0
                        vs_down_count += 1
                    x = appdynamics_class
                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.%s' %(vs_name, metric_name)
                    x.value = metric_value
                    x.timestamp = int(time.time())
                    appdynamics_class_list.append(x)
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.count', vs_count, int(time.time()))
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.status_up', vs_up_count, int(time.time()))
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.status_down', vs_down_count, int(time.time()))
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.status_disabled', vs_disabled_count, int(time.time()))
            send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vs_oper_status completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vs_oper_status encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)



    #-----------------------------------
    #----- RETRIEVE THE NUMBER OF ENABLED, ACTIVE, AND TOTAL POOL MEMBERS FOR EACH VIRTUAL SERVER
    def vs_active_pool_members(self):
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            for t in self.tenants:
                avi_api = 'pool-inventory?page_size=1000'
                pool_member_status = self.avi_request(avi_api,t['name']).json()
                if pool_member_status['count'] > 0:
                    vs_dict= {}
                    virtual_services = self.avi_request('virtualservice?page_size=1000',t['name']).json()
                    if virtual_services['count'] !=0:
                        for v in virtual_services['results']:
                            vs_uuid = v['uuid']
                            vs_name = v['name']
                            vs_dict[vs_uuid] = vs_name
                    for p in pool_member_status['results']:
                        try:
                            vs_list = []
                            if 'num_servers' in p['runtime']:
                                if 'virtualservice' in p:
                                    vs_list.append(p['virtualservice']['name'].replace('.','_'))
                                elif 'virtualservices' in p:
                                    for v in p['virtualservices']:
                                        vs_list.append(vs_dict[v.rsplit('/',1)[1].replace('.','_')])
                                pool_name = p['config']['name'].replace('.','_')
                                pool_members_up = p['runtime']['num_servers_up']
                                pool_members_enabled = p['runtime']['num_servers_enabled']
                                pool_members = p['runtime']['num_servers']
                                for vs_entry in vs_list:
                                    class appdynamics_class(): pass #----- class will be used to create a list for optimized graphite metric sending
                                    x = appdynamics_class
                                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.pool.%s.%s' %(vs_entry, pool_name, 'pool_members_enabled')
                                    x.value = pool_members_enabled
                                    x.timestamp = int(time.time())
                                    appdynamics_class_list.append(x)
                                    class appdynamics_class(): pass #----- class will be used to create a list for optimized graphite metric sending
                                    y = appdynamics_class
                                    y.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.pool.%s.%s' %(vs_entry, pool_name, 'pool_members_up')
                                    y.value = pool_members_up
                                    y.timestamp = int(time.time())
                                    appdynamics_class_list.append(y)
                                    class appdynamics_class(): pass #----- class will be used to create a list for optimized graphite metric sending
                                    z = appdynamics_class
                                    z.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.pool.%s.%s' %(vs_entry, pool_name, 'pool_members')
                                    z.value = pool_members
                                    z.timestamp = int(time.time())
                                    appdynamics_class_list.append(z)
                        except:
                            exception_text = traceback.format_exc()
                            logging.exception(self.avi_controller+': '+exception_text)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vs_active_pool_members completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vs_active_pool_members encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    #-----------------------------------
    #----- get significant log count for current VS
    def vs_sig_log_count(self,v,tenant):
        try:
                temp_start_time = time.time()
                class appdynamics_class(): pass
                vs_name = v['config']['name'].replace('.','_')
                vs_uuid = v['uuid']
                avi_api = 'analytics/logs?type=1&virtualservice=%s&duration=60' %vs_uuid
                resp = self.avi_request(avi_api,tenant).json()
                if 'count' in resp:
                    log_count = resp['count']
                    send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.%s' %(vs_name, 'significant_log_count'), log_count, int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func vs_sig_log_count completed, executed in '+temp_total_time+' seconds')

        except:
            logging.exception(self.avi_controller+': func vs_sig_log_count encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    def vs_sig_log_count_threaded(self):
        try:
            temp_start_time = time.time()
            for t in self.tenants:
                virtual_services = self.avi_request('virtualservice-inventory?page_size=1000',t['name']).json()['results']
                proc = []
                for v in virtual_services:
                    p = Process(target = self.vs_sig_log_count, args = (v,t['name'],))
                    p.start()
                    proc.append(p)
                for p in proc:
                    p.join()
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vs_sig_log_count_threaded completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vs_sig_log_count_threaded encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    #-----------------------------------
    #----- called by service_engine_stats function
    def se_vnic_portgroup(self,appdynamics_class_list,tenant):
        try:
            se_vnic_info = self.avi_request('vimgrsevmruntime',tenant).json()['results']
            for s in se_vnic_info:
                se_name = s['name']
                number_of_ints = len(s['guest_nic'])
                quarantined_int = 0
                avi_internal = 0
                for n in s['guest_nic']:
                    if n['mgmt_vnic'] == True:
                        number_of_ints -= 1
                    elif n['network_name'] == 'Avi Internal':
                        avi_internal += 1
                    elif n['network_name'] == 'quarantine':
                        quarantined_int += 1
                if quarantined_int > 0:
                    class appdynamics_class(): pass
                    x = appdynamics_class
                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.%s' %(se_name, 'quarantined_vnics')
                    x.value = quarantined_int
                    x.timestamp = int(time.time())
                    appdynamics_class_list.append(x)
                elif avi_internal == number_of_ints:
                    class appdynamics_class(): pass
                    x = appdynamics_class
                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.%s' %(se_name, 'aci_vnic_program_error')
                    x.value = 1
                    x.timestamp = int(time.time())
                    appdynamics_class_list.append(x)
        except:
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)



    #-----------------------------------
    #----- called by service_engine_stats function
    def se_missed_hb(self,srvc_engn_list,appdynamics_class_list):
        try:
            for s in srvc_engn_list['results']:
                if 'hb_status' in s:
                    class appdynamics_class(): pass
                    x = appdynamics_class
                    se_name = s['name']
                    x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.%s' %(se_name.replace('.','_'), 'missed_heartbeats')
                    x.value = s['hb_status']['num_hb_misses']
                    x.timestamp = int(time.time())
                    appdynamics_class_list.append(x)
        except:
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def cluster_status(self):
        try:
            temp_start_time = time.time()
            cluster_status = self.avi_request('cluster/runtime','admin').json()
            appdynamics_class_list = []
            active_members = 0
            #-----------------------------------
            #---- RETURN CLUSTER MEMBER ROLE
            #---- follower = 0, leader = 1
            for c in cluster_status['node_states']:
                class appdynamics_class: pass
                if c['state'] == 'CLUSTER_ACTIVE':
                    active_members = active_members + 1
                if c['role'] == 'CLUSTER_FOLLOWER':
                    member_role = 0
                elif c['role'] == 'CLUSTER_LEADER':
                    member_role = 1
                try:
                    member_name = socket.gethostbyaddr(c['name'])[0].replace('.','_')
                except:
                    member_name = c['name'].replace('.','_')
                x = appdynamics_class
                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.cluster.%s.role' %member_name
                x.value = member_role
                x.timestamp = int(time.time())
                appdynamics_class_list.append(x)
            #-----------------------------------
            #---- ADD ACTIVE MEMBER COUNT TO LIST
            class appdynamics_class: pass
            x = appdynamics_class
            x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.cluster.active_members'
            x.value = active_members
            x.timestamp = int(time.time())
            appdynamics_class_list.append(x)
            send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func cluster_status completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func cluster_status encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def vcenter_status(self):
        try:
            temp_start_time = time.time()
            vcenter_status = self.avi_request('vimgrvcenterruntime','admin').json()
            for v in vcenter_status['results']:
                try:
                    vcenter_name = socket.gethostbyaddr(v['vcenter_url'])[0].replace('.','_')
                except:
                    vcenter_name = v['vcenter_url'].replace('.','_')
                if v['inventory_state'] == 'VCENTER_DISCOVERY_COMPLETE':
                    discovery_status = 2
                elif v['inventory_progress'] == 'Initial State':
                    discovery_status = 1
                else:
                    discovery_status = 0
                if v['vcenter_connected'] == True:
                    vcenter_connected = 2
                else:
                    vcenter_connected = 0
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.vcenter.%s.discovery_status' %vcenter_name, discovery_status, int(time.time()))
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.vcenter.%s.vcenter_connected' %vcenter_name, vcenter_connected, int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func vcenter_status completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vcenter_status encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def vcenter_monitor_counters(self): #----- This API was removed in 17.2.4
        try:
            #----- Only run this function every 5 minutes
            if (datetime.now().minute)%5 == 0:
                temp_start_time = time.time()
                vcenter_monitor_counters = self.avi_request('vinfra/internal','admin').json()
                for v in vcenter_monitor_counters:
                    try:
                        vcenter_name = socket.gethostbyaddr(v['vcenter_url'])[0].replace('.','_')
                    except:
                        vcenter_name = v['vcenter_url'].replace('.','_')
                    vm_mon_ver = v['datacenters'][0]['vm_monitor_list_ver']
                    res_mon_ver = v['datacenters'][0]['resource_monitor_list_ver']
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.vcenter.%s.vm_monitor_ver' %vcenter_name, vm_mon_ver, int(time.time()))
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.vcenter.%s.res_monitor_ver' %vcenter_name, res_mon_ver, int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func vcenter_monitor_counters completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func vcenter_monitor_counters encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def apic_status(self):
        if self.avi_request('cloud', 'admin').json()['results'][0]['apic_mode'] == True:
            try:
                temp_start_time = time.time()
                apic_ip = self.avi_request('cloud','admin').json()['results'][0]['apic_configuration']['apic_name'][0]
                try:
                    apic_name = socket.gethostbyaddr(apic_ip)[0].replace('.','_')
                except:
                    apic_name = apic_ip.replace('.','_')
                apic_info = self.avi_request('apic/internal','admin').json()[0]
                if apic_info['connected'] == True:
                    apic_connection_status = 2
                else:
                    apic_connection_status = 0
                if apic_info['websocket_connected'] == True:
                    apic_websocket_status = 2
                else:
                    apic_websocket_status = 0
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.apic.%s.connection_status' %apic_name, apic_connection_status, int(time.time()))
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.apic.%s.websocket_status' %apic_name, apic_websocket_status, int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func apic_status completed, executed in '+temp_total_time+' seconds')
            except:
                logging.exception(self.avi_controller+': func apic_status encountered an error')
                exception_text = traceback.format_exc()
                logging.exception(self.avi_controller+': '+exception_text)
        else:
            if enable_debug == True:
                _1=1




    #-----------------------------------
    def avi_subnet_usage(self):
        try:
            temp_start_time = time.time()
            subnets = self.avi_request('networkruntime?page_size=1000','admin').json()['results']
            appdynamics_class_list = []
            if len(subnets) > 0:
                for s in subnets:
                    if 'subnet_runtime' in s.keys():
                        class appdynamics_class(): pass
                        x = appdynamics_class
                        network_name = s['name'].replace('|','_').replace(':','_').replace('.','-')
                        pool_size = float(s['subnet_runtime'][0]['total_ip_count'])
                        pool_used = float(s['subnet_runtime'][0]['used_ip_count'])
                        percentage_used = int((pool_used/pool_size)*100)
                        x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.networks.%s.used' %network_name
                        x.value = percentage_used
                        x.timestamp = int(time.time())
                        appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func avi_subnet_usage completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func avi_subnet_usage encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def expiring_certs(self): #--- Look for certs that expire within 30 days
        try:
            temp_start_time = time.time()
            current_time = datetime.today()
            appdynamics_class_list = []
            for t in self.tenants:
                ssl_certs = self.avi_request('sslkeyandcertificate?page_size=1000',t['name']).json()
                if ssl_certs['count'] > 0:
                    for s in ssl_certs['results']:
                        class appdynamics_class(): pass
                        x = appdynamics_class()
                        cert_name = s['name'].replace('.','_')
                        if 'not_after' in s['certificate']:
                            expires = datetime.strptime(s['certificate']['not_after'],"%Y-%m-%d %H:%M:%S")
                            days_to_expire = (expires - current_time).days
                        elif s['certificate']['expiry_status'] == 'SSL_CERTIFICATE_EXPIRED':
                            days_to_expire = 0
                        if days_to_expire <= 30:
                            x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.sslcerts.%s.expires' %cert_name
                            x.value = days_to_expire
                            x.timestamp = int(time.time())
                            appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func expiring_certs completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func expiring_certs encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def esx_srvc_engn_vs_count(self):
        try:
            temp_start_time = time.time()
            vm_esx_dict = {}
            page_number = 1
            loop = True
            while loop == True:
                resp = self.avi_request('vimgrhostruntime?page_size=1000&page='+str(page_number),'admin').json()
                if 'error' in resp:
                    loop = False
                else:
                    esx_results = resp['results']
                    for e in esx_results:
                        esx_name = e['name'].replace('.','_')
                        if 'vm_refs' in e:
                            for v in e['vm_refs']:
                                vm_uuid = v.rsplit('/',1)[1]
                                vm_esx_dict[vm_uuid] = esx_name
                    page_number +=1
            discovered_vs = []
            srvc_engn_dict = {}
            for t in self.tenants:
                srvc_engn_list = self.avi_request('serviceengine',t['name']).json()['results']
                for entry in srvc_engn_list:
                    if 'consumers' in entry.keys():
                        for v in entry['consumers']:
                            if entry['name']+v['con_uuid'] not in discovered_vs:
                                discovered_vs.append(entry['name']+v['con_uuid'])
                                if entry['name'] not in srvc_engn_dict:
                                    srvc_engn_dict[entry['name']] = 1
                                else:
                                    srvc_engn_dict[entry['name']] +=1
                    elif 'vs_uuids' in entry.keys(): #---- 17.2.4 api changed
                        for v in entry['vs_uuids']:
                            if entry['name']+v.rsplit('api/virtualservice/')[1] not in discovered_vs:
                                discovered_vs.append(entry['name']+v.rsplit('api/virtualservice/')[1])
                                if entry['name'] not in srvc_engn_dict:
                                    srvc_engn_dict[entry['name']] = 1
                                else:
                                    srvc_engn_dict[entry['name']] +=1
                    else:
                        if entry['name'] not in srvc_engn_dict:
                            srvc_engn_dict[entry['name']] = 0
            esx_vs_se_count = {}
            for s in srvc_engn_dict.keys():
                resp = self.avi_request('vimgrvmruntime?name='+s,'admin').json()
                if resp['count'] != 0:
                    vm_uuid = resp['results'][0]['uuid']
                    esx_host = vm_esx_dict[vm_uuid]
                    if esx_host not in esx_vs_se_count:
                        esx_vs_se_count[esx_host]={'se':1, 'vs':srvc_engn_dict[s]}
                    else:
                        esx_vs_se_count[esx_host]['se'] +=1
                        esx_vs_se_count[esx_host]['vs'] += srvc_engn_dict[s]
            appdynamics_class_list = []
            for server in esx_vs_se_count:
                class appdynamics_class(): pass
                x = appdynamics_class
                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.esx.%s.count.serviceengine' %server
                x.value = esx_vs_se_count[server]['se']
                x.timestamp = int(time.time())
                appdynamics_class_list.append(x)
                class appdynamics_class(): pass
                y = appdynamics_class
                y.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.esx.%s.count.virtualservice' %server
                y.value = esx_vs_se_count[server]['vs']
                y.timestamp = int(time.time())
                appdynamics_class_list.append(y)
            send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func esx_srvc_engn_vs_count completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func esx_srvc_engn_vs_count encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    def virtual_service_hosted_se(self):
        try:
            temp_start_time = time.time()
            vs_dict = {}
            appdynamics_class_list = []
            discovered = []
            for t in self.tenants:
                virtual_services = self.avi_request('virtualservice?page_size=1000',t['name']).json()
                if virtual_services['count'] > 0:
                    for v in virtual_services['results']:
                        vs_dict[v['uuid']] = v['name'].replace('.','_')
            for t in self.tenants:
                service_engines = self.avi_request('serviceengine?page_size=1000',t['name']).json()
                if service_engines['count'] > 0:
                    for s in service_engines['results']:
                        se_name = s['name']
                        if 'consumers' in s:
                            for e in s['consumers']:
                                vs_name = vs_dict[e['con_uuid']].replace('.','_')
                                class appdynamics_class(): pass
                                x = appdynamics_class
                                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.serviceengine.%s' %(vs_name, se_name.replace('.','_'))
                                x.value = 1
                                if x not in discovered:
                                    discovered.append(x)
                                    x.timestamp = int(time.time())
                                    appdynamics_class_list.append(x)
                        elif 'vs_uuids' in s: #---- 17.2.4 api changed
                            for e in s['vs_uuids']:
                                vs_name = vs_dict[e.rsplit('api/virtualservice/')[1]].replace('.','_')
                                class appdynamics_class(): pass
                                x = appdynamics_class
                                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.serviceengine.%s' %(vs_name, se_name.replace('.','_'))
                                x.value = 1
                                if x not in discovered:
                                    discovered.append(x)
                                    x.timestamp = int(time.time())
                                    appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func virtual_service_hosted_se completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func virtual_service_hosted_se encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    #-----------------------------------
    def license_usage(self):
        try:
            temp_start_time = time.time()
            licensing = self.avi_request('licenseusage?limit=365&step=86400','admin').json()
            lic_cores = licensing['licensed_cores']
            if lic_cores != None:
                cores_used = licensing['num_se_vcpus']
                percentage_used = (cores_used / float(lic_cores))*100
                name_space = 'avi.'+self.avi_controller.replace('.','_')+'.licensing.licensed_cores'
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.licensing.licensed_cores', lic_cores, int(time.time()))
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.licensing.cores_used', cores_used, int(time.time()))
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.licensing.percentage_used', percentage_used, int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func license_usage completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func license_usage encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    #-----------------------------------
    def service_engine_vs_capacity(self):
        try:
            temp_start_time = time.time()
            appdynamics_class_list = []
            se_group_max_vs = {}
            discovered_vs = []
            se_dict = {}
            for t in self.tenants:
                se_groups = self.avi_request('serviceenginegroup',t['name']).json()['results']
                for g in se_groups:
                    se_group_max_vs[g['url']] = float(g['max_vs_per_se'])
            for t in self.tenants:
                service_engines = self.avi_request('serviceengine?page_size=1000',t['name']).json()
                if service_engines['count'] > 0:
                    for s in service_engines['results']:
                        se_name = s['name']
                        if se_name not in se_dict:
                            max_vs = se_group_max_vs[s['se_group_ref']]
                            se_dict[se_name]={'max_vs': max_vs, 'total_vs':0}
                        if 'consumers' in s:
                            for v in s['consumers']:
                                if se_name+v['con_uuid'] not in discovered_vs:
                                    discovered_vs.append(s['name']+v['con_uuid'])
                                    se_dict[se_name]['total_vs'] += 1
                        elif 'vs_uuids' in s:
                            for v in s['vs_uuids']:
                                if se_name+v.rsplit('api/virtualservice/')[1] not in discovered_vs:
                                    discovered_vs.append(s['name']+v.rsplit('api/virtualservice/')[1])
                                    se_dict[se_name]['total_vs'] += 1
            for entry in se_dict:
                vs_percentage_used = (se_dict[entry]['total_vs']/se_dict[entry]['max_vs'])*100
                class appdynamics_class(): pass
                x = appdynamics_class
                x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.vs_capacity_used' %entry.replace('.','_')
                x.value = vs_percentage_used
                x.timestamp = int(time.time())
                appdynamics_class_list.append(x)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func service_engine_vs_capacity completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func service_engine_vs_capacity encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)





    #-----------------------------------
    def full_client_log_check(self):
        try:
            temp_start_time = time.time()
            vs_full_log_count = 0 #---- NOT USING, can cleanup
            for t in self.tenants:
                virtual_services = self.avi_request('virtualservice?page_size=1000',t['name']).json()
                if virtual_services['count'] >0:
                    for v in virtual_services['results']:
                        if 'analytics_policy' in v.keys():
                            if 'full_client_logs' in v['analytics_policy'].keys():
                                if v['analytics_policy']['full_client_logs']['enabled'] == True:
                                    vs_full_log_count += 1 #---- NOT USING, can cleanup
                                    send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.full_client_logs' %v['name'].replace('.','_'), 1, int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func full_client_log_check completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func full_client_log_check encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    #-----------------------------------
    def debug_vs_check(self):
        try:
            temp_start_time = time.time()
            for t in self.tenants:
                virtual_services = self.avi_request('debugvirtualservice?page_size=1000',t['name']).json()
                if virtual_services['count'] >0:
                    for v in virtual_services['results']:
                        if 'flags' in v.keys():
                            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.debug_enabled' %v['name'].replace('.','_'), 1, int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func debug_vs_check completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func debug_vs_check encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    #-----------------------------------
    def debug_se_check(self):
        try:
            temp_start_time = time.time()
            discovered_ses = []
            for t in self.tenants:
                service_engines = self.avi_request('debugserviceengine?page_size=1000',t['name']).json()
                if service_engines['count'] >0:
                    for s in service_engines['results']:
                        if s['name'] not in discovered_ses:
                            discovered_ses.append(s['name'])
                            if 'flags' in s.keys():
                                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.serviceengine.%s.debug_enabled' %s['name'].replace('.','_'), 1, int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func debug_vs_check completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func debug_vs_check encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    #-----------------------------------
    def esx_core_usage(self):
        try:
            temp_start_time = time.time()
            esx_host_core = {}
            seg = self.avi_request('serviceenginegroup','admin').json()['results']
            for g in seg:
                if 'vcenter_clusters' in g:
                    for v in g['vcenter_clusters']['cluster_refs']:
                        r1 = self.avi_request(v.split('api/')[1],'admin').json()
                        for h in r1['host_refs']:
                            r2 = self.avi_request(h.split('api/')[1],'admin').json()
                            esx_name = r2['name'].replace('.','_')
                            cpu_cores = r2['num_cpu_cores']
                            if h not in esx_host_core:
                                temp_dict = {}
                                temp_dict['name'] = esx_name
                                temp_dict['total_cpu_cores'] = cpu_cores
                                temp_dict['se_cpu_cores'] = 0
                                esx_host_core[h] = temp_dict
            if len(esx_host_core) > 1:
                se = self.avi_request('serviceengine','admin').json()['results']
                for s in se:
                    esx_host_core[s['host_ref']]['se_cpu_cores'] += s['resources']['num_vcpus']
                if len(esx_host_core) > 0:
                    for entry in esx_host_core:
                        send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.esx.%s.total_cpu_cores' %esx_host_core[entry]['name'], esx_host_core[entry]['total_cpu_cores'], int(time.time()))
                        send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.esx.%s.se_cpu_cores' %esx_host_core[entry]['name'], esx_host_core[entry]['se_cpu_cores'], int(time.time()))
                temp_total_time = str(time.time()-temp_start_time)
                if enable_debug == True:
                    logging.info(self.avi_controller+': func esx_core_usage completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func esx_core_usage encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)


    #-----------------------------------
    def license_expiration(self):
        try:
            current_time = datetime.today()
            temp_start_time = time.time()
            licenses = self.avi_request('license','admin').json()
            for l in licenses['licenses']:
                license_id = l['license_id']
                try:
                    expires = datetime.strptime(l['valid_until'],"%Y-%m-%d %H:%M:%S")
                except:
                    expires = datetime.strptime(l['valid_until'],"%Y-%m-%dT%H:%M:%S")
                days_to_expire = (expires - current_time).days
                send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.licensing.expiration_days.'+license_id, days_to_expire, int(time.time()))
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': func license_expiration completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func license_expiration encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)



    #-----------------------------------
    #----- GET AVI SOFTWARE VERSION NUMBER AND ASSIGN VALUE OF 1
    def get_avi_version(self):
        try:
            temp_start_time = time.time()
            current_version = self.avi_request('version/controller', 'admin').json()[0]['version'].split(' ',1)[0].replace('.','_')
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.current_version.%s' %current_version, 1, int(time.time()))
            if enable_debug == True:
                temp_total_time = str(time.time()-temp_start_time)
                logging.info(self.avi_controller+': func get_avi_version completed, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': get_avi_version encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




    #-----------------------------------
    #----- GET Pool Member specific statistics
    def pool_server_metrics(self):
        try:
            temp_start_time = time.time()
            pool_server_metric_list = [
                'l4_server.max_rx_pkts_absolute',
                'l4_server.avg_rx_pkts',
                'l4_server.max_tx_pkts_absolute',
                'l4_server.avg_tx_pkts',
                'l4_server.max_rx_bytes_absolute',
                'l4_server.max_tx_bytes_absolute',
                'l4_server.avg_bandwidth',
                'l7_server.avg_complete_responses',
                'l4_server.avg_new_established_conns',
                'l4_server.avg_pool_open_conns',
                'l4_server.avg_pool_complete_conns',
                'l4_server.avg_open_conns',
                'l4_server.max_open_conns']
            pool_server_metric_list = ','.join(pool_server_metric_list)
            appdynamics_class_list = []
            discovered_servers = [] #--- this is used b/c members in admin show up in other tenants
            try:
                for t in self.tenants:
                    payload = {
                        "metric_requests": [
                            {
                                "step": 300,
                                "limit": 1,
                                "aggregate_entity": False,
                                "entity_uuid": "*",
                                "obj_id": "*",
                                "pool_uuid": "*",
                                "id": "collItemRequest:AllServers",
                                "metric_id": pool_server_metric_list
                            }
                            ]}
                    api_url = 'analytics/metrics/collection?pad_missing_data=false&dimension_limit=1000&include_name=true&include_refs=true'
                    resp = self.avi_post(api_url,t['name'],payload)
                    if len(resp.json()['series']['collItemRequest:AllServers']) != 0:
                        for p in resp.json()['series']['collItemRequest:AllServers']:
                            if p not in discovered_servers:
                                discovered_servers.append(p)
                                server_object = p.split(',')[2]
                                for d in resp.json()['series']['collItemRequest:AllServers'][p]:
                                    if 'data' in d:
                                        pool_name = d['header']['pool_ref'].rsplit('#',1)[1]
                                        vs_name = d['header']['entity_ref'].rsplit('#',1)[1]
                                        metric_name = d['header']['name'].replace('.','_')
                                        class appdynamics_class(): pass
                                        x = appdynamics_class
                                        x.name_space = 'avi.'+self.avi_controller.replace('.','_')+'.virtualservice.%s.pool.%s.%s.%s' %(vs_name.replace('.','_'), pool_name.replace('.','_'), server_object.replace('.','_'),metric_name)
                                        x.value = d['data'][0]['value']
                                        x.timestamp = int(time.time())
                                        appdynamics_class_list.append(x)
            except:
                logging.exception(self.avi_controller+': func pool_server_metrics encountered an error for tenant '+t['name'])
                exception_text = traceback.format_exc()
                logging.exception(+self.avi_controller+': '+exception_text)
            if len(appdynamics_class_list) > 0:
                send_class_list_appdynamics(appdynamics_class_list)
            temp_total_time = str(time.time()-temp_start_time)
            if enable_debug == True:
                logging.info(self.avi_controller+': pool_server_metrics, executed in '+temp_total_time+' seconds')
        except:
            logging.exception(self.avi_controller+': func pool_server_metrics encountered an error encountered an error')
            exception_text = traceback.format_exc()
            logging.exception(self.avi_controller+': '+exception_text)




#-----------------------------------
#-----------------------------------
#-----------------------------------

    #-----------------------------------
    #----- This is the method within the class that will execute the other methods.
    #----- all test methods will need to be added to test_functions list to be executed
    def gather_metrics(self):
        try:
            start_time = time.time()
            self.login = self.avi_login()
            self.tenants = self.login.json()['tenants']
            #-----------------------------------
            #----- Add Test functions to list for threaded execution
            #-----------------------------------
            test_functions = []
            test_functions.append(self.srvc_engn_vs_count)
            test_functions.append(self.srvc_engn_count)
            test_functions.append(self.srvc_engn_stats)
            test_functions.append(self.srvc_engn_dispatcher_cpu_usage)
            test_functions.append(self.se_bgp_peer_state)
            test_functions.append(self.virtual_service_stats_threaded)
            test_functions.append(self.vs_metrics_per_se_threaded)
            test_functions.append(self.vs_healthscores)
            test_functions.append(self.vs_oper_status)
            test_functions.append(self.vs_sig_log_count_threaded)
            test_functions.append(self.vs_active_pool_members)
            test_functions.append(self.cluster_status)
            test_functions.append(self.vcenter_status)
            #test_functions.append(self.vcenter_monitor_counters) #----- This API was removed in 17.2.4
            test_functions.append(self.apic_status)
            test_functions.append(self.avi_subnet_usage)
            test_functions.append(self.expiring_certs)
            test_functions.append(self.esx_srvc_engn_vs_count)
            test_functions.append(self.virtual_service_hosted_se)
            test_functions.append(self.license_usage)
            test_functions.append(self.service_engine_vs_capacity)
            test_functions.append(self.full_client_log_check)
            test_functions.append(self.debug_vs_check)
            test_functions.append(self.debug_se_check)
            test_functions.append(self.esx_core_usage)
            test_functions.append(self.license_expiration)
            test_functions.append(self.get_avi_version)
            test_functions.append(self.pool_server_metrics)
            #-----------------------------------
            #-----------------------------------
            #-----
            #-----------------------------------
            #----- BEGIN Running Test Functions
            #-----------------------------------
            proc = []
            for f in test_functions:
                p = Process(target = f, args = ())
                p.start()
                proc.append(p)
            for p in proc:
                p.join()
            #-----------------------------------
            #-----
            #-----------------------------------
            #----- Log time it took to execute script
            #-----------------------------------
            total_time = str(time.time()-start_time)
            logging.info(self.avi_controller+': controller specific tests have completed, executed in '+total_time+' seconds')
            send_value_appdynamics('avi.'+self.avi_controller.replace('.','_')+'.metricscript.executiontime', float(total_time)*1000, int(time.time()))
        except:
            _1=1
            logging.exception('Unable to login to: '+self.avi_controller)


    #--- THIS METHOD KICKS OFF THE EXECUTION
    def run(self):
        self.gather_metrics()



    #-----------------------------------
    #-----------------------------------
    #-----------------------------------


#--- Primary function to execute the metrics gathering
#--- This function will create a avi_metrics object for each controller
#--- and kick off the metrics gathering for them.
def main():
    start_time = time.time()
    #---- setup logging
    if logging_enabled == True:
        #----- Disable requests and urlib3 logging
        logging.getLogger("requests").setLevel(logging.WARNING)
        try:
            urllib3_log = logging.getLogger("urllib3")
            urllib3_log.setLevel(logging.CRITICAL)
        except:
            _1=1
        if enable_debug != False:
            logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%b %d %H:%M:%S',filename=log_file,level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%b %d %H:%M:%S',filename=log_file,level=logging.ERROR)
    proc = []
    for entry in avi_controller_list:
        avi_controller = entry['avi_controller']
        host_location = entry['location']
        host_environment = entry['environment']
        c = avi_metrics(avi_controller, host_location, host_environment, entry['avi_user'], isBase64(entry['avi_pass']))
        p = Process(target = c.run, args = ())
        p.start()
        proc.append(p)
    for p in proc:
        p.join()
    total_time = str(time.time()-start_time)
    logging.info('AVI_SCRIPT: metric script has completed, executed in '+total_time+' seconds')





#----- START SCRIPT EXECUTION
fdir = os.path.abspath(os.path.dirname(__file__))
#----- Import avi controller info from json file
with open(os.path.join(fdir,'avi_controllers.json')) as amc:
    avi_controller_list = json.load(amc)['controllers']
main()