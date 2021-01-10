from client import Client

client = Client()


@client.event(name='test')
async def handle_test(*args, **kwargs) -> None:
    print(args, kwargs)


client.run()
