FROM php:8.2-cli-alpine

WORKDIR /app

# 1. pacotes de build + linux-headers + sockets
RUN apk add --no-cache linux-headers $PHPIZE_DEPS git libxml2-dev \
    && docker-php-ext-install sockets \
    && apk del $PHPIZE_DEPS

# 2. composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# 3. dependências PHP
COPY composer.json composer.lock* ./
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress

# 4. código-fonte (inclusive index.php)
COPY . .

EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "index.php"]
