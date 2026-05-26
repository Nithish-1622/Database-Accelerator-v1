from django import forms

from .models import AudioUpload
from .utils.validators import validate_audio_file


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioUpload
        fields = ['filename', 'audio_file', 'file_path', 'file_size', 'duration', 'status', 'processing_stage']

    def clean_audio_file(self):
        uploaded_file = self.cleaned_data['audio_file']
        validation = validate_audio_file(uploaded_file)
        if not validation['valid']:
            raise forms.ValidationError(validation['message'])
        return uploaded_file