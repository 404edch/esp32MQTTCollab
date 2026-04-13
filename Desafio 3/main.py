# main.py Aplicacao MQTT no microcontrolador
# Execute este arquivo pelo Thonny (Run > Run current script)
import network
from umqtt.robust import MQTTClient
from machine import Pin, PWM
import time
import json
import random
import dht
from hcsr04 import HCSR04
import _thread as thread

#==== CONFIGURACOES ALTERE AQUI ====
SSID = "Wokwi-GUEST"            # <-- Wi-Fi: nome da rede
SENHA = ""          # <-- Wi-Fi: senha
BROKER = "mqtt-dashboard.com"
PORTA = 1883
CLIENT_ID = "micro-pucpr-2312312312asd"        # Use seu RA para evitar conflito
TOPICO_PUBLICAR = "bel/micro/dados1" # Micro publica aqui
TOPICO_ASSINAR = "bel/pc/comandos1"  # Micro recebe daqui
QOS = 1

#====================================
sensor = dht.DHT22(Pin(22))
led = Pin(23, Pin.OUT) 
led_estado = False
ultrasonco = HCSR04(trigger_pin=18, echo_pin=19, echo_timeout_us=10000)
buzzer = PWM(Pin(32, Pin.OUT))
buzzer.duty(0)

alerta_proximidade = False
alerta_temperatura = False
alerta_umidade = False
emergencia = False
thread_running = False
lock = False

#==== Conexao Wi-Fi ====
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

def callback_mensagem(topico, mensagem):
    global lock, alerta_temperatura, alerta_umidade, alerta_proximidade, emergencia
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f" [MICRO] Recebido em '{topico}': {payload}")
    
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        
        if comando == "lock":
            print("Trancado")
            lock = True

        elif comando == "unlock":
            print("Destrancado")
            lock = False

        elif comando == "emergencia_comecar":
            print("Emergencia iniciada")
            emergencia = True

        elif comando == "emergencia_parar":
            print("Emergencia parada")
            emergencia = False

        elif comando == "status":
            publicar_dados_sensor()

        else:
            print(f" [MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f" [MICRO] Erro ao processar: {e}")

#---- Funcoes de publicacao ----
def publicar_dados_sensor():
    if emergencia:
        dados = {
            "estado" : "Risco de descongelamento, alarme ativo!",
            "alerta de temperatura" : alerta_temperatura,
            "temperatura": sensor.temperature(),
            "alerta de umidade" : alerta_umidade,
            "umidade": sensor.humidity(),
            "alerta de movimento de carga" : alerta_proximidade,
            "proximidade": ultrasonco.distance_cm()
        }
    else:
        dados = {
            "estado" : "Ambiente estavel.",
            "temperatura": sensor.temperature(),
            "umidade": sensor.humidity(),
            "proximidade": ultrasonco.distance_cm()
        }
    msg = json.dumps(dados)
    client.publish(TOPICO_PUBLICAR, msg, qos=QOS)
    print(f" [MICRO] Dados publicados: {msg}")

def verificar_estado():
    global alerta_proximidade, alerta_temperatura, alerta_umidade, emergencia
    distancia = ultrasonco.distance_cm()
    temperatura = sensor.temperature()
    umidade = sensor.humidity()
    if (distancia <= 100):
        alerta_proximidade = True
        emergencia = True
    else:
        alerta_proximidade = False

    if (temperatura > -5):
        alerta_temperatura = True
        emergencia = True
    else:
        alerta_temperatura = False

    if (umidade > 80):
        alerta_umidade = True
        emergencia = True
    else:
        alerta_umidade = False

def emergencia_led():
    global thread_running
    thread_running = True
    while emergencia:
        led.value(not led.value())
        time.sleep(1)
    led.off()
    thread_running = False

def buzz(freq,tempo):
    buzzer.freq(freq)
    buzzer.duty(10) 
    time.sleep(tempo)   

def alarme_som():
    global thread_running
    thread_running = True
    while (emergencia):
        for freq in range(400, 650, 6):
            buzz(freq, 0.05)
        for freq in range(650, 400, -6):
            buzz(freq, 0.05)
    buzzer.duty(0)
    thread_running = False

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
        if emergencia and not thread_running:
            thread.start_new_thread(emergencia_led, ())
            thread.start_new_thread(alarme_som, ())
        # Verifica novas mensagens (nao-bloqueante)
        client.check_msg()
        sensor.measure()
        if not lock:
            verificar_estado()
        # A cada 30 segundos, publica dados automaticamente
            contador += 1
            if emergencia:
                if contador >= 10:
                    publicar_dados_sensor()
                    contador = 0
            elif contador >= 30:
                publicar_dados_sensor()
                contador = 0
            
                
        time.sleep(1)
except KeyboardInterrupt:
    print("\n [MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print(" [MICRO] Desconectado do broker.")