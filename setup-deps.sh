#!/bin/bash -e

TARGET_DIR=src/SimpleRichTradingJournal/things
cd "$(dirname "$0")"
mkdir -p $TARGET_DIR
cd $TARGET_DIR

curl -o 52_bootstrap.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
curl -o 51_codemirror.css https://cdn.jsdelivr.net/npm/codemirror@5.65.16/lib/codemirror.css
curl -o 11_codemirror.js https://cdn.jsdelivr.net/npm/codemirror@5.65.16/lib/codemirror.js
curl -o 12_markdown.js https://cdn.jsdelivr.net/npm/codemirror@5.65.16/mode/markdown/markdown.js
curl -o 13_closebrackets.js https://cdn.jsdelivr.net/npm/codemirror@5.65.16/addon/edit/closebrackets.js
curl -o 14_matchbrackets.js https://cdn.jsdelivr.net/npm/codemirror@5.65.16/addon/edit/matchbrackets.js
