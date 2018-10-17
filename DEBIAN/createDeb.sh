#!/bin/bash

cp ../asteroides.py games-in-pygame/usr/local/games
cp asteroides    games-in-pygame/usr/local/games
chmod 755  games-in-pygame/usr/local/games/asteroides
dpkg-deb --build games-in-pygame
