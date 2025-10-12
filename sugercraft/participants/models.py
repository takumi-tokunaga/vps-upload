from django.db import models

# Create your models here.
class Participant(models.Model):
    name = models.CharField(max_length=100)
    game_id = models.CharField(max_length=100, primary_key=True)  # MinecraftのゲームIDを一意の識別子として使用
    uuid = models.CharField(max_length=36)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class SNSLink(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='sns_links')
    platform = models.CharField(max_length=50)  # 例: Twitter, YouTube, etc.
    url = models.URLField()

    def __str__(self):
        return f"{self.participant.name} - {self.platform}"
    
class StreamLink(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='stream_links')
    platform = models.CharField(max_length=50)  # 例: Twitch, YouTube Live, etc.
    url = models.URLField()

    def __str__(self):
        return f"{self.participant.name} - {self.platform}"