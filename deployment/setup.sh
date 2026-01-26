#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Iniciando instalación del Bot de Trading...${NC}"

# Detectar gestor de paquetes (apt para Ubuntu, dnf/yum para Oracle Linux)
if command -v apt &> /dev/null; then
    echo "Sistema detectado: Debian/Ubuntu"
    sudo apt update
    sudo apt install -y python3-venv python3-pip git
elif command -v dnf &> /dev/null; then
    echo "Sistema detectado: Oracle Linux / RHEL"
    sudo dnf install -y python3 python3-pip git
else
    echo "Sistema no soportado automáticamente. Asegúrate de tener Python 3.8+ instalado."
fi

# Crear directorio si no existe
mkdir -p bot-trading
cd bot-trading

# Crear entorno virtual
echo -e "${GREEN}Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo -e "${GREEN}Instalando dependencias...${NC}"
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "AVISO: No se encontró requirements.txt. Asegúrate de subir los archivos del proyecto."
fi

# Configurar servicio systemd
echo -e "${GREEN}Configurando servicio systemd...${NC}"
sudo cp ../deployment/bot.service /etc/systemd/system/kraken-bot.service
sudo systemctl daemon-reload
sudo systemctl enable kraken-bot

echo -e "${GREEN}¡Instalación completada!${NC}"
echo "Para subir tus archivos locales, usa SCP desde tu máquina local:"
echo "scp -r * ubuntu@TU_IP_PUBLICA:/home/ubuntu/bot-trading/"
echo ""
echo "Luego inicia el bot con: sudo systemctl start kraken-bot"
