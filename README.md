Aplicação está em Docker.

Para rodar a aplicação precisamos rodar

docker compose up -d

##  Testes rápidos via **cURL**

```bash
#  Gera uma leitura de sensores (GET)
curl -X GET http://localhost:3000/sensor-data

# Disparar um alerta síncrono (POST)
curl -X POST http://localhost:3000/alert \
     -H "Content-Type: application/json" \
     -d '{"msg":"Pressão acima do limiar!"}'

# Criar um despacho logístico na fila RabbitMQ (POST)
curl -X POST http://localhost:8000/dispatch \
     -H "Content-Type: application/json" \
     -d '{"equipment":"Válvula de segurança","priority":"Alta"}'

#  Lista os equipamentos simulados (GET)
curl -X GET http://localhost:8000/equipments

# Consulta  histórico de eventos (GET)
curl -X GET http://localhost:5000/events
```

-------------------------


## O que cada API faz e como executá-la?


API NODE (3000) – A API faz a simulção da leitura de sensores de temperatura e da pressão em poços de petróleo. Ela tem dois endpoints principais:
*	GET /sensor-data: Ele gera e retorna dados simulados. Estes dados são armazenados em cache no Redis para evitar consultas repetidas no curto prazo.
*	POST /alert: envia um alerta crítico via HTTP para a API de eventos (Python).
A API é executada dentro do Docker. Depois de subir a stack com o comando docker compose up, ela fica disponível em http://localhost:3000. (iniciada com o comando no Dockerfile node app.js)

 API (Python + Flask) (5000) – A API registra e retorna alertas recebidos da API Node.js e consome mensagens da fila do RabbitMQ (enviadas pela API PHP).
*	POST /event: recebe os alertas e salva no Redis em uma lista (events:list).
*	GET /events: retorna a lista de eventos críticos armazenados.
*	Ele Também possui um consumer que escuta a fila RabbitMQ e adiciona as mensagens recebidas à mesma lista de eventos.
A API é executada automaticamente no Docker se for rodar manualmente:
(python app.py)
API PHP – A API simula a gestão de equipamentos e envio de ordens de transporte:
*	GET /equipments: retorna uma lista fictícia de equipamentos.
*	POST /dispatch: envia uma mensagem para a fila RabbitMQ, que será consumida pela API de eventos.
A API é executada automaticamente no Docker se for rodar manualmente:
(php -S localhost:8000)


## Como elas se comunicam?

Sensores (Node.js) → Eventos Críticos (Python)
Quando a API de sensores detecta uma condição crítica, ela manda um alerta via HTTP POST para o endpoint /event da API Python.
Exemplo: POST http://events-python:5000/event

Logística (PHP) → Eventos Críticos (Python)
A API de logística publica uma mensagem na fila RabbitMQ (logistics) quando receber uma ordem de despacho.
A API Python possui um consumer em background que escuta esta fila e registra o evento como se fosse mais um alerta crítico.

Redis como cache compartilhado:
O Redis atua como intermediário dos dados temporários:
*	A API de sensores usa Redis para cachear os dados do /sensor-data.
*	A API de eventos usa Redis para armazenar e buscar a lista de eventos recebidos.

Comunicação em ambiente Docker
Todas as APIs se conectam entre si pelo nome do serviço Docker Compose (sensors-node, events-python, logistics-php). Por exemplo:
*	O PHP publica para o RabbitMQ no host rabbitmq.
*	O Python consome dessa mesma fila, ouvindo o host rabbitmq.

![image](https://github.com/user-attachments/assets/9cf9d372-be9a-4aeb-9475-a42d68f486b5)

## Onde o cache Redis foi usado?
API de Sensores (Node.js)
*      Ao acessar o endpoint GET /sensor-data, os dados simulados de temperatura e pressão ficam armazenados em cache no Redis por um tempo definido (TTL).
*     Isso evita que os mesmos dados sejam gerados repetidamente a cada requisição, melhorando a performance da API.

API de Eventos Críticos (Python)
*      A lista de eventos recebidos (via HTTP ou RabbitMQ) é armazenada em uma lista Redis com a chave events:list.
*      Cada vez que um novo evento chega, a lista no Redis é atualizada.
*      Quando o endpoint GET /events é acessado, os dados são recuperados diretamente do Redis.


## Como a fila RabbitMQ entra no fluxo?

*     A API de Logística (PHP) publica uma mensagem na fila do RabbitMQ sempre que o endpoint POST /dispatch é chamado. Essa mensagem representa uma solicitação urgente de transporte ou entrega de equipamentos.
*     A API de Eventos (Python) possui um consumidor rodando em segundo plano (via consumer.py) que fica escutando esta fila.
*     Quando uma nova mensagem é publicada pela API PHP, o consumidor a recebe automaticamente e a adiciona à lista de eventos críticos no Redis.
*     Dessa forma, a API de Logística não precisa mais esperar a resposta da API Python.




 
