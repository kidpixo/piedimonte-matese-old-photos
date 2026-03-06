#!/bin/sh
set -e

cd /usr/src/app

if [ -f Gemfile ]; then
  bundle check || bundle install
fi

exec "$@"
