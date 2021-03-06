'''
Created on Jul 15, 2016

@author: jivan
'''
from django import forms

class RecordingForm(forms.Form):
    # These attributes make the changes that cause Android devices to open a native
    #    audio recorder for recording, then populate the field with the name of the recorded file
    recording_widget = \
        forms.ClearableFileInput(attrs={'accept': 'audio/*', 'capture': 'microphone'})
    recording = forms.FileField(widget=recording_widget)
    expected_tone = forms.IntegerField(min_value=1, max_value=5, widget=forms.HiddenInput)
