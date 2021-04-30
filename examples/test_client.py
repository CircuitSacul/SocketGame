import asyncio
from socketgame.connection import Connection
import sys
from typing import Any, Dict

import pygame

from socketgame.client import Client

game_data: Dict[Any, Any] = {}

host = input("Server IP Address: ")
port = int(input("Server Port Number: "))

client = Client(host=host, port=port)

pygame.init()
SCREEN = pygame.display.set_mode((500, 500))


def draw() -> None:
    for _, p in game_data['players'].items():
        pygame.draw.circle(
            SCREEN, pygame.Color('red'),
            (p['x'], p['y']), 25, 0
        )


@client.event(name='set_data')
async def set_data(con: Connection, data: Dict[Any, Any]) -> None:
    print("setting data")
    global game_data
    game_data = data


@client.task
async def game_loop() -> None:
    while game_data == {}:
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
            client.send('move', {'x': x, 'y': y})

        draw()
        await asyncio.sleep(0.01)

        pygame.display.update()


client.run()
