import uuid

from django.db import models


def audio_upload_path(instance, filename):
    return f'audio/{instance.id}/{filename}'


class AudioUpload(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        QUEUED = 'queued', 'Queued'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class ProcessingStage(models.TextChoices):
        VALIDATION = 'validation', 'Validation'
        STORAGE = 'storage', 'Storage'
        QUEUED = 'queued', 'Queued'
        PREPROCESSING = 'preprocessing', 'Preprocessing'
        TRANSCRIPTION = 'transcription', 'Transcription'
        KEYWORD_EXTRACTION = 'keyword_extraction', 'Keyword Extraction'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to=audio_upload_path, max_length=500)
    file_path = models.CharField(max_length=1024)
    file_size = models.PositiveBigIntegerField(default=0)
    duration = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.UPLOADED, db_index=True)
    processing_stage = models.CharField(
        max_length=64,
        choices=ProcessingStage.choices,
        default=ProcessingStage.VALIDATION,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'processing_stage']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.filename} ({self.id})'


class TranscriptModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio = models.ForeignKey(AudioUpload, related_name='transcripts', on_delete=models.CASCADE, db_index=True)
    transcript = models.TextField()
    model_name = models.CharField(max_length=64, default='whisper-small')
    language = models.CharField(max_length=32, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['audio', 'created_at'])]

    def __str__(self):
        return f'Transcript<{self.audio_id}>'


class KeywordModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio = models.ForeignKey(AudioUpload, related_name='keywords', on_delete=models.CASCADE, db_index=True)
    keyword = models.CharField(max_length=255, db_index=True)
    frequency = models.IntegerField(default=0)
    timestamps = models.JSONField(blank=True, null=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-frequency', '-created_at']
        indexes = [models.Index(fields=['keyword', 'frequency']), models.Index(fields=['audio'])]

    def __str__(self):
        return f'{self.keyword} ({self.frequency}) for {self.audio_id}'


class FrequencyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio = models.ForeignKey(AudioUpload, related_name='frequencies', on_delete=models.CASCADE, db_index=True)
    keyword = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('audio', 'keyword')
        indexes = [models.Index(fields=['audio', 'keyword'])]

    def __str__(self):
        return f'{self.keyword}:{self.count}@{self.audio_id}'


class ClusterModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio = models.ForeignKey(AudioUpload, related_name='clusters', on_delete=models.CASCADE, db_index=True)
    algorithm = models.CharField(max_length=64, default='kmeans')
    parameters = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['audio', 'algorithm'])]

    def __str__(self):
        return f'Cluster<{self.id}> for {self.audio_id} ({self.algorithm})'


class ClusterMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cluster = models.ForeignKey(ClusterModel, related_name='members', on_delete=models.CASCADE, db_index=True)
    keyword = models.ForeignKey(KeywordModel, related_name='cluster_members', on_delete=models.CASCADE, null=True)
    keyword_text = models.CharField(max_length=255, blank=True, default='')
    weight = models.FloatField(default=0.0)

    class Meta:
        indexes = [models.Index(fields=['cluster', 'keyword'])]

    def __str__(self):
        return f'{self.keyword_text} ({self.weight}) in {self.cluster_id}'