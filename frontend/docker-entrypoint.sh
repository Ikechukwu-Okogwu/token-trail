#!/bin/sh
# Install deps if node_modules missing (e.g. when bind-mounting), then run dev server
if [ ! -d "node_modules" ]; then
  npm install
fi
exec npm run dev
