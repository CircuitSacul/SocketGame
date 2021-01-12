import asyncio
from server import Server


host = input("Host: ")
port = int(input("Port: "))

server = Server(host=host, port=port)

game_data = {'players': {}}
# Structure: {'players': {id: {'x': x_pos, 'y': y_pos}, ...}}


@server.on_ready
async def on_ready() -> None:
    print(f"Server open at {server.host}:{server.port}")


@server.on_connection
async def on_connect(con) -> None:
    game_data['players'][con.id] = {'x': 0, 'y': 0}
    print("Client Connected:", con.id)


@server.on_disconnect
async def on_disconnect(con) -> None:
    del game_data['players'][con.id]
    print("Client Disconnected:", con.id)


@server.event(name='move')
async def on_player_move(con, data) -> None:
    x_move = data['x']
    y_move = data['y']
    if x_move < -1 or x_move > 1:
        return
    if y_move < -1 or y_move > 1:
        return

    game_data['players'][con.id]['x'] += x_move
    game_data['players'][con.id]['y'] += y_move


@server.task
async def send_data() -> None:
    while True:
        for client in server.clients:
            client.send('set_data', game_data)
        await asyncio.sleep(0.01)


server.run()
