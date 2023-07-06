import paho.mqtt.client as mqtt

# Define as informações de conexão do servidor MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

# Cria um objeto cliente MQTT
client = mqtt.Client()

# Define a função de callback para o recebimento das mensagens
def on_message(client, userdata, message):
    # Exibe a mensagem recebida na tela
    print(f'GOT: {message.payload.decode("utf-8")}%')

# Conecta o cliente ao servidor MQTT e se inscreve no tópico "uso-de-memoria"
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe('herbalia')

# Define a função de callback para o recebimento das mensagens
client.on_message = on_message

# Inicia o loop de espera por mensagens
client.loop_forever()