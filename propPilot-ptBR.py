import sqlite3
from datetime import datetime
import os
import re
import subprocess
import sys
import smtplib
from email.mime.text import MIMEText
import json
import csv

# --- Funções de Instalação de Dependências ---

def instalar_dependencias():
    """Instala bibliotecas necessárias se elas não estiverem instaladas."""
    dependencias = ['colorama', 'tabulate']
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ Biblioteca '{dep}' já está instalada.")
        except ImportError:
            print(f"Instalando a biblioteca '{dep}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ Biblioteca '{dep}' instalada com sucesso!")
            except subprocess.CalledProcessError:
                print(f"❌ Erro ao instalar a biblioteca '{dep}'. Por favor, instale manualmente com 'pip install {dep}' e execute o script novamente.")
                sys.exit(1)

instalar_dependencias()

# A partir daqui, as bibliotecas estão garantidas de estarem instaladas
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Inicializa o colorama para funcionar em todos os sistemas
init(autoreset=True)

# Cores e estilos para simular um terminal verde antigo
GREEN = Fore.GREEN
BLACK = Back.BLACK
RESET_ALL = Style.RESET_ALL

# Expressão regular para validação de URL
URL_PATTERN = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# --- Funções de Banco de Dados e Lógica do Script ---

def conectar_banco():
    """Conecta ao banco de dados e cria as tabelas se não existirem."""
    conn = sqlite3.connect('gerenciador_propostas.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT UNIQUE,
            telefone TEXT,
            data_cadastro TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS propostas (
            id_proposta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            nome_projeto TEXT NOT NULL,
            descricao_projeto TEXT,
            valor_proposta REAL,
            status INTEGER,
            link_proposta TEXT,
            link_questionario TEXT,
            link_contrato TEXT,
            data_envio TEXT,
            data_atualizacao TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respostas_padronizadas (
            id_resposta INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            assunto TEXT,
            conteudo TEXT
        )
    """)

    conn.commit()
    return conn, cursor

def is_valid_url(url):
    """Verifica se a string é uma URL válida."""
    if not url:
        return True
    return re.match(URL_PATTERN, url) is not None

def ler_config():
    """Lê as configurações de um arquivo JSON."""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {}

def salvar_config(config):
    """Salva as configurações em um arquivo JSON."""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def configurar_email():
    """Guia o usuário para configurar as credenciais de e-mail."""
    print(GREEN + "\n--- Configuração de E-mail ---" + RESET_ALL)
    print(GREEN + "Para enviar e-mails, precisamos de algumas informações." + RESET_ALL)
    print(GREEN + "Se for Gmail, você precisará de uma 'senha de app'. Veja como gerar: https://bit.ly/3gY4jYk" + RESET_ALL)
    
    email_remetente = input(GREEN + "Seu e-mail: " + RESET_ALL)
    senha = input(GREEN + "Sua senha de app: " + RESET_ALL)
    smtp_server = input(GREEN + "Servidor SMTP (ex: smtp.gmail.com): " + RESET_ALL)
    smtp_port = input(GREEN + "Porta SMTP (ex: 587): " + RESET_ALL)

    config = {
        "email_remetente": email_remetente,
        "senha_email": senha,
        "smtp_server": smtp_server,
        "smtp_port": int(smtp_port)
    }

    salvar_config(config)
    print(GREEN + "✅ Configuração de e-mail salva com sucesso!" + RESET_ALL)

def enviar_email(destinatario, assunto, corpo):
    """Envia um e-mail usando as configurações salvas."""
    config = ler_config()
    if not config:
        print(GREEN + "❌ Erro: Configurações de e-mail não encontradas. Por favor, configure-as primeiro." + RESET_ALL)
        return False
    
    try:
        msg = MIMEText(corpo)
        msg['Subject'] = assunto
        msg['From'] = config['email_remetente']
        msg['To'] = destinatario

        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['email_remetente'], config['senha_email'])
            server.send_message(msg)
        
        print(GREEN + f"✅ E-mail enviado com sucesso para {destinatario}!" + RESET_ALL)
        return True
    except Exception as e:
        print(GREEN + f"❌ Erro ao enviar e-mail: {e}" + RESET_ALL)
        return False

def menu_conteudos(conn, cursor):
    """Sub-menu para gerenciar conteúdos (respostas padronizadas) e enviar e-mail."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(GREEN + "--- Menu de Conteúdos e E-mail ---" + RESET_ALL)
        print(GREEN + "[1] Adicionar nova resposta padronizada" + RESET_ALL)
        print(GREEN + "[2] Visualizar respostas padronizadas" + RESET_ALL)
        print(GREEN + "[3] Enviar e-mail com template" + RESET_ALL)
        print(GREEN + "[0] Voltar" + RESET_ALL)
        
        opcao = input(GREEN + "\nEscolha uma opção: " + RESET_ALL)
        
        if opcao == '1':
            adicionar_resposta_padronizada(conn, cursor)
        elif opcao == '2':
            visualizar_respostas_padronizadas(cursor)
        elif opcao == '3':
            enviar_email_com_template(conn, cursor)
        elif opcao == '0':
            break
        else:
            print(GREEN + "❌ Opção inválida." + RESET_ALL)
        
        input(GREEN + "\nPressione Enter para continuar..." + RESET_ALL)

def enviar_email_com_template(conn, cursor):
    """Prepara e envia um e-mail a partir de um template e um cliente."""
    print(GREEN + "\n--- Enviar E-mail com Template ---" + RESET_ALL)
    try:
        id_resposta = int(input(GREEN + "ID do template de resposta: " + RESET_ALL))
        id_cliente = int(input(GREEN + "ID do cliente para o qual enviar: " + RESET_ALL))

        cursor.execute("SELECT assunto, conteudo FROM respostas_padronizadas WHERE id_resposta = ?", (id_resposta,))
        template = cursor.fetchone()
        
        cursor.execute("SELECT nome_completo, email FROM clientes WHERE id_cliente = ?", (id_cliente,))
        cliente = cursor.fetchone()

        if not template or not cliente:
            print(GREEN + "❌ Erro: Template ou Cliente não encontrados." + RESET_ALL)
            return

        assunto = template[0].replace("[nome_cliente]", cliente[0])
        corpo = template[1].replace("[nome_cliente]", cliente[0])
        
        enviar_email(cliente[1], assunto, corpo)
    except ValueError:
        print(GREEN + "❌ Erro: ID do template e do cliente devem ser números." + RESET_ALL)

def exportar_para_csv(conn, cursor):
    """Exporta dados de uma tabela para um arquivo CSV."""
    print(GREEN + "\n--- Exportar para CSV ---" + RESET_ALL)
    print(GREEN + "[1] Exportar Clientes" + RESET_ALL)
    print(GREEN + "[2] Exportar Propostas" + RESET_ALL)
    escolha = input(GREEN + "Escolha uma opção (1 ou 2): " + RESET_ALL)

    if escolha == '1':
        tabela = 'clientes'
        nome_arquivo = 'clientes.csv'
        cursor.execute("SELECT * FROM clientes")
    elif escolha == '2':
        tabela = 'propostas'
        nome_arquivo = 'propostas.csv'
        cursor.execute("SELECT * FROM propostas")
    else:
        print(GREEN + "❌ Opção inválida." + RESET_ALL)
        return
    
    headers = [desc[0] for desc in cursor.description]
    dados = cursor.fetchall()

    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(dados)
    
    print(GREEN + f"✅ Dados da tabela '{tabela}' exportados para '{nome_arquivo}' com sucesso!" + RESET_ALL)


def menu_utilidades(conn, cursor):
    """Sub-menu para configurações e utilidades."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(GREEN + "--- Menu de Utilidades ---" + RESET_ALL)
        print(GREEN + "[1] Configurar e-mail" + RESET_ALL)
        print(GREEN + "[2] Exportar dados para CSV" + RESET_ALL)
        print(GREEN + "[0] Voltar" + RESET_ALL)
        
        opcao = input(GREEN + "\nEscolha uma opção: " + RESET_ALL)
        
        if opcao == '1':
            configurar_email()
        elif opcao == '2':
            exportar_para_csv(conn, cursor)
        elif opcao == '0':
            break
        else:
            print(GREEN + "❌ Opção inválida." + RESET_ALL)
        
        input(GREEN + "\nPressione Enter para continuar..." + RESET_ALL)

# Outras funções (adicionar_cliente, visualizar_propostas, buscar_dados, etc.) ...
# (código das outras funções do script anterior deve ser mantido aqui)

# --- Interface de Menu Principal ---

def menu_principal():
    """Loop principal que exibe o menu e gerencia as ações do usuário."""
    conn, cursor = conectar_banco()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BLACK + GREEN + "=" * 40)
        print(GREEN + "  Gerenciador de Propostas DevJC v4.0  ")
        print("=" * 40 + RESET_ALL)
        print(GREEN + "\nO que você gostaria de fazer hoje?" + RESET_ALL)
        print(GREEN + "[1] Registrar novo cliente" + RESET_ALL)
        print(GREEN + "[2] Registrar nova proposta" + RESET_ALL)
        print(GREEN + "[3] Visualizar todas as propostas" + RESET_ALL)
        print(GREEN + "[4] Atualizar status de uma proposta" + RESET_ALL)
        print(GREEN + "[5] Gerar relatório de desempenho" + RESET_ALL)
        print(GREEN + "[6] Buscar dados (cliente ou projeto)" + RESET_ALL)
        print(GREEN + "[7] Gerenciar Conteúdos e E-mail" + RESET_ALL)
        print(GREEN + "[8] Configurações e Utilidades" + RESET_ALL)
        print(GREEN + "[0] Sair" + RESET_ALL)

        opcao = input(GREEN + "\nEscolha uma opção: " + RESET_ALL)

        if opcao == '1':
            adicionar_cliente(conn, cursor)
        elif opcao == '2':
            adicionar_proposta(conn, cursor)
        elif opcao == '3':
            visualizar_propostas(cursor)
        elif opcao == '4':
            atualizar_status_proposta(conn, cursor)
        elif opcao == '5':
            gerar_relatorio(cursor)
        elif opcao == '6':
            buscar_dados(cursor)
        elif opcao == '7':
            menu_conteudos(conn, cursor)
        elif opcao == '8':
            menu_utilidades(conn, cursor)
        elif opcao == '0':
            print(GREEN + "👋 Obrigado por usar o gerenciador! Até mais!" + RESET_ALL)
            break
        else:
            print(GREEN + "❌ Opção inválida. Tente novamente." + RESET_ALL)
        
        if opcao in ['1', '2', '4', '7', '8']:
            input(GREEN + "\nPressione Enter para continuar..." + RESET_ALL)
        elif opcao not in ['0', '3', '5', '6']:
            input(GREEN + "\nPressione Enter para continuar..." + RESET_ALL)

    conn.close()

if __name__ == "__main__":
    menu_principal()
