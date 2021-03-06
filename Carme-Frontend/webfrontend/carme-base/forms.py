# ---------------------------------------------- 
# Carme
# ----------------------------------------------
# forms.py                                                                                                                                                                     
#                                                                                                                                                                                                            
# see Carme development guide for documentation: 
# * Carme/Carme-Doc/DevelDoc/CarmeDevelopmentDocu.md
#
# Copyright 2019 by Fraunhofer ITWM  
# License: http://open-carme.org/LICENSE.md 
# Contact: info@open-carme.org
# ---------------------------------------------
from django import forms
from .models import Images

""" admin messages
    # NOTE: deprecated

"""
class MessageForm(forms.Form):
    message = forms.CharField(label='Message', max_length=500)

""" delete admin messages
    # NOTE: deprecated
"""
class DeleteMessageForm(forms.Form):
    messageID = forms.DecimalField(required=True, widget=forms.HiddenInput())

""" start user jobs

"""
class StartJobForm(forms.Form):
    def __init__(self, *args, **kwargs):
        image_choices = kwargs.pop('image_choices')
        node_choices = kwargs.pop('node_choices')
        gpu_choices = kwargs.pop('gpu_choices')
        super(StartJobForm, self).__init__(*args, **kwargs)
        self.fields["nodes"] = forms.ChoiceField(
            label='Run on # nodes', choices=node_choices)
        self.fields["gpus"] = forms.ChoiceField(
            label='GPUs per node', choices=gpu_choices)
        self.fields["image"] = forms.ChoiceField(
            label='Start image', choices=image_choices)
        self.fields["name"] = forms.CharField(label='Job name')
        self.fields["name"].initial = str('MyJob')

""" stop jobs

"""
class StopJobForm(forms.Form):
    jobID = forms.DecimalField(required=True, widget=forms.HiddenInput())
    jobName = forms.CharField(required=True, widget=forms.HiddenInput())
    jobUser = forms.CharField(required=True, widget=forms.HiddenInput())

""" job infos

"""
class JobInfoForm(forms.Form):
    jobID = forms.DecimalField(required=True, widget=forms.HiddenInput())

""" change password

"""
class ChangePasswd(forms.Form):
    new_password1 = forms.CharField(
        required=True, label='New Password', widget=forms.PasswordInput())
    new_password2 = forms.CharField(
        required=True, label='Repeat', widget=forms.PasswordInput())
