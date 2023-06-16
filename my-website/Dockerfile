# pull official base image
FROM node:latest

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000

# install dependencies
COPY package.json package-lock.json* ./

RUN npm install

COPY . .
EXPOSE 3000

RUN npm run build

CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0"]
