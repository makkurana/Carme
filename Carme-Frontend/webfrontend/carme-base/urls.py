# ---------------------------------------------- 
# Carme
# ----------------------------------------------
# urls.py                                                                                                                                                                      
#                                                                                                                                                                                                            
# see Carme development guide for documentation: 
# * Carme/Carme-Doc/DevelDoc/CarmeDevelopmentDocu.md
#
# Copyright 2019 by Fraunhofer ITWM  
# License: http://open-carme.org/LICENSE.md 
# Contact: info@open-carme.org
# ---------------------------------------------
from django.urls import path
from django.conf.urls import url, include

from . import views

urlpatterns = [
            path('', views.index, name='index'),
            url(r'^password/$', views.change_password, name='change_password'),
            url(r'^StartJob/$', views.start_job, name='start_job'),
            url(r'^StopJob/$', views.stop_job, name='stop_job'),
            url(r'^JobInfo/$', views.job_info, name='job_info'),
            url(r'^JobTable/$', views.job_table, name='job_table'),
            url(r'^JobHist/$', views.job_hist, name='job_hist'),
            url(r'^auth/$', views.auth, name='job_auth'),
            url(r'^AdminJobTable/$', views.admin_job_table, name='admin_job_table'),
	    url(r'^AdminClusterStatus/$', views.admin_cluster_status, name='admin_cluster_status'), 
            url(r'^ImageTable/$', views.image_table, name='image_table'),
            url(r'^TimeOut/$', views.time_out, name='time_out'),
            url(r'^maintenance-mode/', include('maintenance_mode.urls')),
            url(r'^line_chart/$', views.line_chart, name='line_chart'),
            url(r'^line_chart_json/$', views.line_chart_json, name='line_chart_json'),
            url(r'^Messages/$', views.messages, name='messages'), 
            ]
