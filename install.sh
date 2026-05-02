#!/bin/bash

# Script de instalação do Sistema de Controladoria
# Autor: Sistema Auditoria
# Data: 11/11/2025

echo "=========================================="
echo "  Instalador - Sistema de Controladoria"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para printar mensagens coloridas
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar se Python 3 está instalado
print_info "Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não está instalado. Por favor, instale Python 3 primeiro."
    exit 1
fi
print_success "Python 3 encontrado: $(python3 --version)"

# Verificar se venv está disponível
print_info "Verificando módulo venv..."
if ! python3 -m venv --help &> /dev/null; then
    print_error "Módulo venv não encontrado. Instalando python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi
print_success "Módulo venv disponível"

# Criar ambiente virtual
VENV_PATH="$HOME/meuambiente"
if [ -d "$VENV_PATH" ]; then
    print_info "Ambiente virtual já existe em $VENV_PATH"
    read -p "Deseja recriar o ambiente virtual? (s/N): " resposta
    if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
        print_info "Removendo ambiente virtual antigo..."
        rm -rf "$VENV_PATH"
        print_info "Criando novo ambiente virtual..."
        python3 -m venv "$VENV_PATH"
        print_success "Ambiente virtual recriado"
    fi
else
    print_info "Criando ambiente virtual em $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    print_success "Ambiente virtual criado"
fi

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
source "$VENV_PATH/bin/activate"
print_success "Ambiente virtual ativado"

# Atualizar pip
print_info "Atualizando pip..."
pip install --upgrade pip --quiet
print_success "pip atualizado"

# Instalar dependências Python
print_info "Instalando dependências Python..."
echo ""

# Lista de dependências
DEPENDENCIES=(
    "Django==5.2.8"
    "psycopg2-binary"
    "python-dotenv"
    "bleach"
    "django-encrypted-model-fields"
    "cryptography"
)

for dep in "${DEPENDENCIES[@]}"; do
    print_info "Instalando $dep..."
    pip install "$dep" --quiet
    if [ $? -eq 0 ]; then
        print_success "$dep instalado"
    else
        print_error "Falha ao instalar $dep"
        exit 1
    fi
done

echo ""
print_success "Todas as dependências instaladas com sucesso!"

# Verificar se PostgreSQL está instalado
print_info "Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL não encontrado."
    print_info "Por favor, instale o PostgreSQL:"
    echo "    sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi
print_success "PostgreSQL encontrado"

# Criar banco de dados se não existir
print_info "Verificando banco de dados..."
DB_EXISTS=$(psql -lqt | cut -d \| -f 1 | grep -w controladoria_db)
if [ -z "$DB_EXISTS" ]; then
    print_info "Criando banco de dados 'controladoria_db'..."
    createdb controladoria_db 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Banco de dados criado"
    else
        print_error "Não foi possível criar o banco de dados automaticamente"
        print_info "Execute manualmente: createdb controladoria_db"
    fi
else
    print_success "Banco de dados 'controladoria_db' já existe"
fi

# Navegar para o diretório do projeto
PROJECT_DIR="$HOME/Controladoria/Controladoria"
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Diretório do projeto não encontrado: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar arquivo .env
print_info "Verificando arquivo .env..."
if [ ! -f "config/.env" ]; then
    print_error "Arquivo .env não encontrado em config/.env"
    print_info "Por favor, crie o arquivo config/.env com as configurações necessárias"
    exit 1
fi
print_success "Arquivo .env encontrado"

# Executar migrações
print_info "Executando migrações do banco de dados..."
python manage.py makemigrations
python manage.py migrate

if [ $? -eq 0 ]; then
    print_success "Migrações executadas com sucesso"
else
    print_error "Erro ao executar migrações"
    exit 1
fi

# Criar superusuário (opcional)
echo ""
print_info "Deseja criar um superusuário agora?"
read -p "(s/N): " criar_super

if [ "$criar_super" = "s" ] || [ "$criar_super" = "S" ]; then
    python manage.py createsuperuser
fi

# Resumo da instalação
echo ""
echo "=========================================="
echo "  ✓ Instalação Concluída com Sucesso!"
echo "=========================================="
echo ""
print_success "Ambiente virtual: $VENV_PATH"
print_success "Diretório do projeto: $PROJECT_DIR"
print_success "Banco de dados: controladoria_db"
echo ""
echo "Para iniciar o servidor de desenvolvimento:"
echo ""
echo "  1. Ative o ambiente virtual:"
echo "     source $VENV_PATH/bin/activate"
echo ""
echo "  2. Navegue até o diretório do projeto:"
echo "     cd $PROJECT_DIR"
echo ""
echo "  3. Inicie o servidor:"
echo "     python manage.py runserver 0.0.0.0:8000"
echo ""
echo "  4. Acesse no navegador:"
echo "     http://127.0.0.1:8000/"
echo ""
print_info "Usuário master já criado:"
echo "     Username: admin"
echo "     Senha: Admin@123"
echo ""
echo "=========================================="
