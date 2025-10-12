import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .views import server_status_get
from .models import Participant

class ParticipantConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # サーバーステータスを取得してクライアントに送信
        server_status = await database_sync_to_async(server_status_get)()
        participants_data = await self.get_participants_data(server_status)
        
        await self.send(text_data=json.dumps({
            'server_status': server_status,
            'online_participants': participants_data['online'],
            'offline_participants': participants_data['offline'],
        }))

    @database_sync_to_async
    def get_participants_data(self, server_status):
        participants = Participant.objects.all()
        def participant_to_dict(participant):
            return {
                'name': participant.name,
                'game_id': participant.game_id,
                'uuid': participant.uuid,
                'bio': participant.bio,
                'sns_links': [
                    {'platform': link.platform, 'url': link.url}
                    for link in participant.sns_links.all()
                ],
                'stream_links': [
                    {'platform': link.platform, 'url': link.url}
                    for link in participant.stream_links.all()
                ]
            }
        if server_status['online'] and server_status['players']:
            online_player_names = [player['name'] for player in server_status['players']]
            online_participants = participants.filter(game_id__in=online_player_names)
            offline_participants = participants.exclude(game_id__in=online_player_names)
        else:
            online_participants = []
            offline_participants = participants
        return {
            'online': [participant_to_dict(p) for p in online_participants],
            'offline': [participant_to_dict(p) for p in offline_participants]
        }