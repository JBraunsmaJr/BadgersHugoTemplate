FROM alpine

# Copying the golang from golang's alpine image
# So that it works in ours!
COPY --from=golang:alpine /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"

RUN apk update && \
    apk upgrade && \
    apk add git
        

# Let's install hugo, and initialize a default project!
RUN apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community hugo && \
    hugo new site default-blogsite && \
    mkdir /blogsite 

COPY entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

# Windows does crazy things... 
RUN sed -i 's/\r$//' entrypoint.sh

WORKDIR /blogsite

ENTRYPOINT ["sh", "/entrypoint.sh"]

# This just lets folks know we have a volume at this path
VOLUME /blogsite

# This is the default hugo port
EXPOSE 1313
EXPOSE 80
EXPOSE 35729