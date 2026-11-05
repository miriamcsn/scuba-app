# nginx sem root: roda com o UID 101 e escuta na porta 8080.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
