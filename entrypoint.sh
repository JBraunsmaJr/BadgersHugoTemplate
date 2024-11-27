#!/bin/sh

if [ -z "$(ls -A /blogsite)" ]; then
    echo "Initializing /blogsite with default content"
    cp -r /default-blogsite/* /blogsite
fi 

cd /blogsite

# Full rebuilds on change
# Must bind to 0.0.0.0 so it binds to all network interfaces in container!!!!
hugo server --disableFastRender --buildDrafts --watch --bind 0.0.0.0 ${THEME_NAME:+-t $THEME_NAME}