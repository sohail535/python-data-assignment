FROM nginx:stable-alpine

COPY services/mock_site /usr/share/nginx/html
COPY services/mock_site/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
