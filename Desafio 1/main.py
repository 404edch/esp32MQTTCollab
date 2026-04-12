# main.py Aplicacao MQTT no microcontrolador
# Execute este arquivo pelo Thonny (Run > Run current script)
import network
from umqtt.robust import MQTTClient
import machine
import time
import json
import random
import dht

#==== CONFIGURACOES ALTERE AQUI ====
SSID = "Wokwi-GUEST"            # <-- Wi-Fi: nome da rede
SENHA = ""          # <-- Wi-Fi: senha
BROKER = "mqtt-dashboard.com"
PORTA = 1883
CLIENT_ID = "micro-pucpr-2312312312asd"        # Use seu RA para evitar conflito
TOPICO_PUBLICAR = "bel/micro/dados1" # Micro publica aqui
TOPICO_ASSINAR = "bel/pc/comandos1"  # Micro recebe daqui
QOS = 0

# LED integrado (ajuste o pino conforme sua placa)
# ESP32: pino 2 | Pico W: pino "LED" | ESP8266: pino 2

sensor = dht.DHT22(machine.Pin(25))
led = machine.Pin(2, machine.Pin.OUT)
led_estado = False

#---- Conexao Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(SSID, SENHA)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            print(f" Tentativa {tentativas}/20...")
    if wlan.isconnected():
        print(f"Wi-Fi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("ERRO: Nao foi possivel conectar ac Wi-Fi")
        return False

# Callback de mensagens recebidas
def callback_mensagem(topico, mensagem):
    global led_estado
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f" [MICRO] Recebido em '{topico}': {payload}")
    
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        
        if comando == "led_on":
            led.value(1)
            led_estado = True
            print("[MICRO] LED ligado!")
            publicar_estado()
        elif comando == "led_off":
            led.value(0)
            led_estado = False
            print(" [MICRO] LED desligado!")
            publicar_estado()
        elif comando == "status":
            publicar_dados_sensor()
        else:
            print(f" [MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f" [MICRO] Erro ao processar: {e}")

#---- Funcoes de publicacao ----
def publicar_estado():
    estado = "ligado" if led_estado else "desligado"
    msg = json.dumps({"led": estado})
    client.publish(TOPICO_PUBLICAR, msg, qos=QOS)
    print(f" [MICRO] Publicado: {msg}")

def publicar_dados_sensor():
    # Simulacao de dados de sensor
    # Em um projeto real, leia sensores reais aqui (DHT22, BMP280, etc.)
    dados = {
        "temperatura": sensor.temperature(),
        "umidade": sensor.humidity(),
        "led": "ligado" if led_estado else "desligado"
    }
    msg = json.dumps(dados)
    client.publish(TOPICO_PUBLICAR, msg, qos=QOS)
    print(f" [MICRO] Dados publicados: {msg}")

# ----- Conexao e loop principal -----
if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit

print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA)
client.set_callback(callback_mensagem)
client.connect(clean_session=False)
print(f" [MICRO] Conectado a {BROKER}")
client.subscribe(TOPICO_ASSINAR, qos=QOS)
print(f" [MICRO] Inscrito em: {TOPICO_ASSINAR}")
print(" [MICRO] Aguardando comandos...\n")

# Loop principal
contador = 0
try:
    while True:
        # Verifica novas mensagens (nao-bloqueante)
        sensor.measure()
        client.check_msg()
        
        # A cada 30 segundos, publica dados automaticamente
       # contador += 1
        if contador >= 30:
            publicar_dados_sensor()
            contador = 0
            
        time.sleep(1)
except KeyboardInterrupt:
    print("\n [MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print(" [MICRO] Desconectado do broker.")