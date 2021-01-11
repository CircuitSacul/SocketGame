import asyncio
import sys

import pygame

from client import Client


SCREEN = pygame.display.set_mode((500, 500))
pygame.init()


game_data = None

host = input("Server IP Address: ")
port = int(input("Server Port Number: "))


client = Client(host=host, port=port)


def draw() -> None:
    for _, p in game_data['players'].items():
        pygame.draw.circle(
            SCREEN, pygame.Color('red'),
            (p['x'], p['y']), 25, 0
        )


@client.event(name='set_data')
async def set_data(con, data) -> None:
    global game_data
    game_data = data


@client.task
async def game_loop() -> None:
    while game_data is None:
        await asyncio.sleep(0.1)

    while True:
        SCREEN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exitting")
                sys.exit()

        x = y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            y = -1
        elif keys[pygame.K_DOWN]:
            y = 1
        if keys[pygame.K_LEFT]:
            x = -1
        elif keys[pygame.K_RIGHT]:
            x = 1

        if any([x != 0, y != 0]):
            client.server.send('move', {'x': x, 'y': y})

        draw()
        await asyncio.sleep(0.01)

        pygame.display.update()


client.run()
