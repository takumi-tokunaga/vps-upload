from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Participant

from mcstatus import JavaServer

# Create your views here.

@login_required
def list(request):
    participants = Participant.objects.all()
    server_status = server_status_get()
    
    online_participants = []
    if server_status['online'] and server_status['players']: #サーバーがオンラインでかつプレイヤーが存在する場合
        # server_status['players']からプレイヤー名のみをonline_player_namesに抽出
        online_player_names = [player['name'] for player in server_status['players']]
        
        # game_idがオンラインプレイヤーに含まれる参加者のみ抽出
        online_participants = participants.filter(game_id__in=online_player_names)
        offline_participants = participants.exclude(game_id__in=online_player_names)
    else:
        online_participants = []
        offline_participants = participants

    # オフライン参加者の辞書型を作成
    def participant_to_dict(participant):
        data = participant.__dict__.copy()
        # Remove _state (Django internal)
        data.pop('_state', None)
        # Add SNSLink and StreamLink info
        data['sns_links'] = [
            {'platform': link.platform, 'url': link.url}
            for link in participant.sns_links.all()
        ]
        data['stream_links'] = [
            {'platform': link.platform, 'url': link.url}
            for link in participant.stream_links.all()
        ]
        return data

    online_participants_dict = [participant_to_dict(p) for p in online_participants]
    offline_participants_dict = [participant_to_dict(p) for p in offline_participants]

    return render(request, 'participants/list.html', {'online': online_participants_dict, 'offline': offline_participants_dict, 'server_status': server_status})


def server_status_get():
    server = JavaServer.lookup("163.44.97.195:25565")
    try:
        status = server.status()
        players_obj = status.players.sample  # オンラインプレイヤーの名前一覧（最大12人）
        players = [player.__dict__ for player in players_obj] if players_obj else []
        context = {
            'online': True,
            'players': players or [],
            'count': status.players.online,
            'max': status.players.max,
        }
    except Exception:
        context = {
            'online': False,
            'players': [],
            'count': 0,
            'max': 0,
        }
    return context