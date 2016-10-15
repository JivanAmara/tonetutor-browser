# Redirect mandarintt.com -> www.mandarintt.com
server {
    listen 66.228.38.188:80;
    listen [2600:3c03::45:8001]:80;

    server_name mandarintt.com;

    location / {
        return 301 http://www.mandarintt.com$request_uri;
    }
}

# Set up non-ssl www.mandarintt.com
server {
    listen 66.228.38.188:80;
    listen [2600:3c03::45:8001]:80;

    server_name www.mandarintt.com;
    client_max_body_size 4G;
    keepalive_timeout 5;

    # Redirect to https for paths starting with '/tutor'
    location ~ /tutor/? {
        return 301 https://$server_name$request_uri;
    }

    # Redirect to https for paths starting with '/accounts'
    location /accounts {
        return 301 https://$server_name$request_uri;
    }

    # Serve all other paths via app proxy
    location / {
            # proxy to app
            try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_read_timeout  240;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        proxy_pass   http://app_server_tonetutor;
    }
}
