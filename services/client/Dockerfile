# build stage
FROM node:lts-alpine as build-stage

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

RUN npm run build

# production stage

FROM node:16.0.0-alpine3.11 as production-stage

RUN npm install pushstate-server -g

WORKDIR /usr/src/app

COPY --from=build-stage /app/dist /usr/src/app

EXPOSE 9000

CMD pushstate-server -d /usr/src/app -p 9000
