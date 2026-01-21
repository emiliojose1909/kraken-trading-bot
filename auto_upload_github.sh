#!/bin/bash

# ============================================
# Script Automático para Subir a GitHub
# ============================================

echo "🚀 Bot de Trading Kraken - Upload a GitHub"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "trading_bot.py" ]; then
    echo -e "${RED}❌ Error: No estás en el directorio kraken_bot${NC}"
    echo "Ejecuta: cd /home/ubuntu/kraken_bot"
    exit 1
fi

echo -e "${BLUE}📦 Verificando repositorio Git...${NC}"
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: No es un repositorio Git${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Repositorio Git encontrado${NC}"
echo ""

# Verificar si ya existe el remote
if git remote | grep -q "origin"; then
    echo -e "${BLUE}🔗 Remote 'origin' ya existe, eliminando...${NC}"
    git remote remove origin
fi

# Agregar remote
echo -e "${BLUE}🔗 Conectando con GitHub...${NC}"
git remote add origin https://github.com/emiliojose1909/kraken-trading-bot.git

echo -e "${GREEN}✓ Remote configurado${NC}"
echo ""

# Mostrar información
echo -e "${BLUE}📊 Información del repositorio:${NC}"
echo "  Rama: $(git branch --show-current)"
echo "  Commits: $(git rev-list --count HEAD)"
echo "  Archivos: $(git ls-files | wc -l)"
echo ""

# Instrucciones para el push
echo -e "${BLUE}📤 Para subir a GitHub, ejecuta:${NC}"
echo ""
echo -e "${GREEN}git push -u origin main${NC}"
echo ""
echo "Cuando pida credenciales:"
echo "  Username: emiliojose1909"
echo "  Password: [Tu Personal Access Token]"
echo ""
echo -e "${BLUE}🔑 Generar token en:${NC}"
echo "  https://github.com/settings/tokens"
echo ""
echo -e "${GREEN}✓ Todo listo para subir${NC}"
