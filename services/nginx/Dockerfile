FROM nginx:1.17.9
EXPOSE 80 443

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/nginx.conf
