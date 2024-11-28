#!/bin/sh

if [ -z "$(ls -A /blogsite)" ]; then
    echo "Initializing /blogsite with default content"
    cp -r /default-blogsite/* /blogsite
fi 

cd /blogsite

# Just to make sure environment variables are properly getting set
echo "Is Deployment: $DEPLOY,  Theme: $THEME"

if [ "$DEPLOY" = "True" ] || [ "$DEPLOY" = "true" ]; then
  echo "Building hugo content..."
  hugo 
else
  # Must bind to 0.0.0.0 so it binds to all network interfaces in container!!!!
  # The poll option is required (for windows at least) - where hugo periodically checks contents to determine if rebuild is needed
  # Build all the things
  hugo server --poll "700ms" --navigateToChanged --disableFastRender --watch=true --bind 0.0.0.0 ${THEME:+-t $THEME}
fi