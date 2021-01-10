from server import Server

server = Server()


@server.event(name='test')
async def handle_test(*args, **kwargs) -> None:
    print(args, kwargs)


server.run()
