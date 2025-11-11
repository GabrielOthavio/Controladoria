# Sistema de Controladoria - Guia de Instalação

## Requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- Git (opcional)

## Instalação Rápida

### Opção 1: Script Automático (Recomendado)

Execute o script de instalação:

```bash
cd /home/aluno/Controladoria
bash install.sh
```

O script irá:
- ✓ Verificar Python 3 e venv
- ✓ Criar ambiente virtual em `~/meuambiente`
- ✓ Instalar todas as dependências
- ✓ Criar banco de dados PostgreSQL
- ✓ Executar migrações
- ✓ Oferecer criação de superusuário

### Opção 2: Instalação Manual

1. **Criar ambiente virtual:**
   ```bash
   python3 -m venv ~/meuambiente
   source ~/meuambiente/bin/activate
   ```

2. **Instalar dependências:**
   ```bash
   cd /home/aluno/Controladoria
   pip install -r requirements.txt
   ```

3. **Criar banco de dados:**
   ```bash
   createdb controladoria_db
   ```

4. **Configurar arquivo .env:**
   
   Certifique-se de que `Controladoria/config/.env` existe e contém:
   ```
   SECRET_KEY='sua_chave_secreta'
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   FIELD_ENCRYPTION_KEY='sua_chave_de_criptografia'
   
   DB_NAME=controladoria_db
   DB_USER=aluno
   DB_PASSWORD=
   DB_HOST=
   DB_PORT=5432
   ```

5. **Executar migrações:**
   ```bash
   cd Controladoria
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Criar superusuário (opcional):**
   ```bash
   python manage.py createsuperuser
   ```

## Executar o Sistema

1. **Ativar ambiente virtual:**
   ```bash
   source ~/meuambiente/bin/activate
   ```

2. **Iniciar servidor:**
   ```bash
   cd /home/aluno/Controladoria/Controladoria
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Acessar no navegador:**
   ```
   http://127.0.0.1:8000/
   ```

## Credenciais Padrão

**Usuário Master:**
- Username: `admin`
- Senha: `Admin@123`
- Perfil: CHEFE

## Dependências Instaladas

- Django 5.2.8
- psycopg2-binary 2.9.11
- python-dotenv 1.2.1
- bleach 6.3.0
- django-encrypted-model-fields 0.6.5
- cryptography 46.0.3

## Estrutura do Projeto

```
Controladoria/
├── install.sh              # Script de instalação automática
├── requirements.txt        # Lista de dependências Python
├── README_INSTALL.md      # Este arquivo
└── Controladoria/
    ├── manage.py
    ├── config/
    │   ├── .env           # Configurações do ambiente
    │   └── settings.py
    └── Auth/
        ├── models.py
        ├── forms.py
        ├── views/
        └── templates/
```

## Solução de Problemas

### Erro: PostgreSQL não encontrado
```bash
sudo apt-get install postgresql postgresql-contrib
```

### Erro: python3-venv não encontrado
```bash
sudo apt-get install python3-venv
```

### Erro: Permissão negada no PostgreSQL
```bash
# Criar banco manualmente
sudo -u postgres createdb controladoria_db
```

### Erro ao instalar psycopg2-binary
```bash
# Instalar dependências do sistema
sudo apt-get install libpq-dev python3-dev
```

## Comandos Úteis

**Recriar banco de dados:**
```bash
dropdb controladoria_db
createdb controladoria_db
python manage.py migrate
```

**Criar novo usuário admin:**
```bash
python manage.py shell
>>> from Auth.models import Usuario
>>> Usuario.objects.create_superuser('usuario', 'email@example.com', 'senha', perfil='CHEFE')
```

**Ver logs do servidor:**
```bash
python manage.py runserver --noreload
```

## Suporte

Para problemas ou dúvidas:
- Verifique os logs do terminal
- Confirme que todas as dependências foram instaladas
- Verifique as configurações do arquivo `.env`
- Certifique-se de que o PostgreSQL está rodando
