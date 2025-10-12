from mcstatus import JavaServer

def online_players(request):
    server = JavaServer.lookup("163.44.97.195:25565")
    try:
        status = server.status()
        players = status.players.sample  # オンラインプレイヤーの名前一覧（最大12人）
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

    print(context)

if __name__ == "__main__":
    online_players(None)