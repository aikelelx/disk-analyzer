#!/bin/bash
mkdir -p ~/.local/bin
cp src/diskanalyzer.py ~/.local/bin/diskanalyzer
chmod +x ~/.local/bin/diskanalyzer
echo "Installation complete"
echo "Usage: diskanalyzer --help"
