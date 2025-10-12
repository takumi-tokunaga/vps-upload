from django.contrib import admin
from .models import Participant, SNSLink, StreamLink

class SNSLinkInline(admin.TabularInline):
	model = SNSLink
	extra = 1

class StreamLinkInline(admin.TabularInline):
	model = StreamLink
	extra = 1

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
	inlines = [SNSLinkInline, StreamLinkInline]

@admin.register(SNSLink)
class SNSLinkAdmin(admin.ModelAdmin):
	list_display = ('participant', 'platform', 'url')

@admin.register(StreamLink)
class StreamLinkAdmin(admin.ModelAdmin):
	list_display = ('participant', 'platform', 'url')
