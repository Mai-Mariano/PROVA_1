<?php
require __DIR__ . '/vendor/autoload.php';
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

$queue = $_ENV['QUEUE'];

$router = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

switch ("$method $router") {
    case 'GET /equipments':
        echo json_encode([
            ['id'=>1,'name'=>'Bomba Submersível','status'=>'available'],
            ['id'=>2,'name'=>'Válvula de Segurança','status'=>'maintenance']
        ]);
        break;

    case 'POST /dispatch':
        $body = json_decode(file_get_contents('php://input'), true) ?: [];
        $conn = AMQPStreamConnection::create_connection([
            ['host'=>'localhost','port'=>5672,'user'=>'guest','password'=>'guest']
        ]);
        $ch = $conn->channel();
        $ch->queue_declare($queue, false, true, false, false);
        $msg = new AMQPMessage(json_encode($body), ['delivery_mode'=>2]);
        $ch->basic_publish($msg, '', $queue);
        $ch->close(); $conn->close();
        http_response_code(201);
        echo json_encode(['queued'=>$body]);
        break;

    default:
        http_response_code(404);
        echo json_encode(['error'=>'Not found']);
}
