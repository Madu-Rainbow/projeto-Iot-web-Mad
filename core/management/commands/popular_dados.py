from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Ambiente, Dispositivo, TipoSensor, Sensor, LeituraSensor
from django.utils import timezone
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nome de usuário para associar os dados (default: admin)',
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário "{username}" não encontrado. Crie o usuário primeiro.')
            )
            return

        self.stdout.write(f'Populando dados para o usuário: {user.username}')

        # Criar tipos de sensores
        tipos_sensores = [
            {'nome': 'Temperatura', 'unidade': '°C', 'descricao': 'Sensor de temperatura ambiente'},
            {'nome': 'Umidade', 'unidade': '%', 'descricao': 'Sensor de umidade relativa do ar'},
            {'nome': 'Luminosidade', 'unidade': 'lux', 'descricao': 'Sensor de luminosidade'},
            {'nome': 'Pressão', 'unidade': 'hPa', 'descricao': 'Sensor de pressão atmosférica'},
            {'nome': 'Movimento', 'unidade': 'bool', 'descricao': 'Sensor de presença/movimento'},
            {'nome': 'pH', 'unidade': 'pH', 'descricao': 'Sensor de pH da água'},
        ]

        for tipo_data in tipos_sensores:
            tipo, created = TipoSensor.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'Tipo de sensor criado: {tipo.nome}')

        # Criar ambientes
        ambientes_data = [
            {'nome': 'Sala de Estar', 'descricao': 'Ambiente principal da casa'},
            {'nome': 'Cozinha', 'descricao': 'Área de preparo de alimentos'},
            {'nome': 'Quarto Principal', 'descricao': 'Dormitório principal'},
            {'nome': 'Jardim', 'descricao': 'Área externa com plantas'},
            {'nome': 'Escritório', 'descricao': 'Local de trabalho'},
        ]

        ambientes = []
        for amb_data in ambientes_data:
            ambiente, created = Ambiente.objects.get_or_create(
                nome=amb_data['nome'],
                usuario=user,
                defaults=amb_data
            )
            ambientes.append(ambiente)
            if created:
                self.stdout.write(f'Ambiente criado: {ambiente.nome}')

        # Criar dispositivos
        dispositivos_data = [
            {'nome': 'ESP32 Sala', 'tipo': 'controlador', 'modelo': 'ESP32-WROOM-32', 'fabricante': 'Espressif', 'mac_address': '24:6F:28:AB:12:34'},
            {'nome': 'Arduino Cozinha', 'tipo': 'controlador', 'modelo': 'Arduino Uno', 'fabricante': 'Arduino', 'mac_address': '24:6F:28:AB:12:35'},
            {'nome': 'Raspberry Pi Jardim', 'tipo': 'gateway', 'modelo': 'Raspberry Pi 4B', 'fabricante': 'Raspberry Pi Foundation', 'mac_address': '24:6F:28:AB:12:36'},
            {'nome': 'NodeMCU Quarto', 'tipo': 'controlador', 'modelo': 'NodeMCU v3', 'fabricante': 'NodeMCU', 'mac_address': '24:6F:28:AB:12:37'},
            {'nome': 'ESP8266 Escritório', 'tipo': 'controlador', 'modelo': 'ESP8266', 'fabricante': 'Espressif', 'mac_address': '24:6F:28:AB:12:38'},
        ]

        dispositivos = []
        for i, disp_data in enumerate(dispositivos_data):
            ambiente = ambientes[i % len(ambientes)]
            disp_data['ambiente'] = ambiente
            disp_data['usuario'] = user
            disp_data['ip_address'] = f'192.168.1.{100 + i}'
            disp_data['status'] = random.choice(['ativo', 'ativo', 'ativo', 'inativo'])  # Maioria ativo
            disp_data['ultimo_contato'] = timezone.now() - timedelta(minutes=random.randint(1, 60))
            
            dispositivo, created = Dispositivo.objects.get_or_create(
                mac_address=disp_data['mac_address'],
                defaults=disp_data
            )
            dispositivos.append(dispositivo)
            if created:
                self.stdout.write(f'Dispositivo criado: {dispositivo.nome}')

        # Criar sensores
        sensores_por_dispositivo = [
            ['Temperatura', 'Umidade'],  # ESP32 Sala
            ['Temperatura', 'Movimento'], # Arduino Cozinha  
            ['Temperatura', 'Umidade', 'pH'], # Raspberry Pi Jardim
            ['Temperatura', 'Luminosidade'], # NodeMCU Quarto
            ['Temperatura', 'Pressão'], # ESP8266 Escritório
        ]

        sensores = []
        for i, dispositivo in enumerate(dispositivos):
            tipos_para_dispositivo = sensores_por_dispositivo[i]
            
            for tipo_nome in tipos_para_dispositivo:
                tipo_sensor = TipoSensor.objects.get(nome=tipo_nome)
                
                sensor_data = {
                    'nome': f'{tipo_nome} - {dispositivo.nome}',
                    'tipo': tipo_sensor,
                    'dispositivo': dispositivo,
                    'ambiente': dispositivo.ambiente,
                    'usuario': user,
                    'ativo': True,
                }
                
                # Configurar valores específicos por tipo
                if tipo_nome == 'Temperatura':
                    sensor_data['valor_minimo'] = -10.0
                    sensor_data['valor_maximo'] = 50.0
                    sensor_data['precisao'] = 1
                elif tipo_nome == 'Umidade':
                    sensor_data['valor_minimo'] = 0.0
                    sensor_data['valor_maximo'] = 100.0
                    sensor_data['precisao'] = 1
                elif tipo_nome == 'Luminosidade':
                    sensor_data['valor_minimo'] = 0.0
                    sensor_data['valor_maximo'] = 1000.0
                    sensor_data['precisao'] = 0
                elif tipo_nome == 'Pressão':
                    sensor_data['valor_minimo'] = 950.0
                    sensor_data['valor_maximo'] = 1050.0
                    sensor_data['precisao'] = 1
                elif tipo_nome == 'pH':
                    sensor_data['valor_minimo'] = 0.0
                    sensor_data['valor_maximo'] = 14.0
                    sensor_data['precisao'] = 2
                
                sensor, created = Sensor.objects.get_or_create(
                    dispositivo=dispositivo,
                    tipo=tipo_sensor,
                    defaults=sensor_data
                )
                sensores.append(sensor)
                if created:
                    self.stdout.write(f'Sensor criado: {sensor.nome}')

        # Criar leituras dos sensores (últimos 7 dias)
        self.stdout.write('Criando leituras dos sensores...')
        
        for sensor in sensores:
            # Criar leituras para os últimos 7 dias
            for dia in range(7):
                for hora in range(0, 24, 2):  # A cada 2 horas
                    timestamp = timezone.now() - timedelta(days=dia, hours=hora)
                    
                    # Gerar valor baseado no tipo de sensor
                    if sensor.tipo.nome == 'Temperatura':
                        base_temp = 22 if sensor.ambiente.nome != 'Jardim' else 18
                        valor = base_temp + random.uniform(-5, 8) + random.uniform(-2, 2)
                    elif sensor.tipo.nome == 'Umidade':
                        valor = random.uniform(40, 80)
                    elif sensor.tipo.nome == 'Luminosidade':
                        # Simular ciclo dia/noite
                        if 6 <= timestamp.hour <= 18:
                            valor = random.uniform(300, 800)
                        else:
                            valor = random.uniform(0, 50)
                    elif sensor.tipo.nome == 'Pressão':
                        valor = random.uniform(1000, 1030)
                    elif sensor.tipo.nome == 'Movimento':
                        valor = random.choice([0, 1])
                    elif sensor.tipo.nome == 'pH':
                        valor = random.uniform(6.5, 8.5)
                    else:
                        valor = random.uniform(0, 100)
                    
                    # Arredondar baseado na precisão
                    valor = round(valor, sensor.precisao)
                    
                    LeituraSensor.objects.create(
                        sensor=sensor,
                        valor=valor,
                        timestamp=timestamp
                    )

        total_leituras = LeituraSensor.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Banco de dados populado com sucesso! Total de leituras: {total_leituras}')
        )
        
        self.stdout.write('\nResumo:')
        self.stdout.write(f'- Tipos de Sensores: {TipoSensor.objects.count()}')
        self.stdout.write(f'- Ambientes: {Ambiente.objects.filter(usuario=user).count()}')
        self.stdout.write(f'- Dispositivos: {Dispositivo.objects.filter(usuario=user).count()}')
        self.stdout.write(f'- Sensores: {Sensor.objects.filter(usuario=user).count()}')
        self.stdout.write(f'- Leituras: {total_leituras}')
        
        self.stdout.write('\nCredenciais de acesso:')
        self.stdout.write(f'- Admin: admin / admin123')
        self.stdout.write(f'- URL Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write(f'- URL Principal: http://127.0.0.1:8000/')