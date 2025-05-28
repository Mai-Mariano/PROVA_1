# logistics-php/Dockerfile
FROM php:8.2-cli-alpine

WORKDIR /app

# ------------------------------------------------------------------
# 1) Pacotes de “build” + linux-headers  (para sockets compilar)
#    $PHPIZE_DEPS já traz autoconf, gcc, g++, make…
# ------------------------------------------------------------------
RUN apk add --no-cache linux-headers $PHPIZE_DEPS git libxml2-dev \
    # ----------------------------------------------------------------
    # 2) compila e habilita a ext/sockets
    # ----------------------------------------------------------------
    && docker-php-ext-install sockets \
    # ----------------------------------------------------------------
    # 3) remove dependências de build p/ deixar a imagem menor
    # ----------------------------------------------------------------
    && apk del $PHPIZE_DEPS

# ------------------------------------------------------------------
# 4) Copiamos o Composer (binário estático) a partir da imagem oficial
# ------------------------------------------------------------------
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# ------------------------------------------------------------------
# 5) Instala as dependências do projeto
# ------------------------------------------------------------------
COPY composer.json .
# (se existir composer.lock, copie também p/ builds reprodutíveis)
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress

# ------------------------------------------------------------------
# 6) Copia o restante do código-fonte
# ------------------------------------------------------------------
COPY . .

EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "index.php"]
