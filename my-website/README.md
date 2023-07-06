# My Documentation

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

CLI:

```sh
npm run install
```

dev run:

```sh
npm run start
```

prod run:

```sh
npm run build
npm run serve
```

Docker(dev):

Use custom image to cache packages:

```sh
docker build -t website-dev -f ./Dockerfile.dev .
docker run -it --rm \
    -v $(pwd):/usr/src/app \
    -v /usr/src/app/node_modules \
    -v /usr/src/app/.docusaurus \
    -w /usr/src/app \
    -p 3000:3000 \
    website-dev \
    npm run start -- --host 0.0.0.0
```

or in one command(`-q` output _final image hash_):

```sh
docker run -it --rm \
    -v $(pwd):/usr/src/app \
    -v /usr/src/app/node_modules \
    -v /usr/src/app/.docusaurus \
    -w /usr/src/app \
    -p 3000:3000 \
    $(docker build -f ./Dockerfile.dev -q .) \
    npm run start -- --host 0.0.0.0
```

No caching packages(using `node` image):

```sh
docker run -it --rm \
    -v $(pwd):/usr/src/app \
    -v /usr/src/app/node_modules \
    -v /usr/src/app/.docusaurus \
    -w /usr/src/app \
    -p 3000:3000 \
    node \
    bash -c "npm install && npm run start"
```

Docker(prod):

Use custom image to bundle app:

```sh
docker build -t website .
docker run -it --rm \
    -p 3000:3000 \
    website
```
