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

# --- Dependency Installation Functions ---

def install_dependencies():
    """Installs required libraries if they are not already installed."""
    dependencies = ['colorama', 'tabulate']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ Library '{dep}' is already installed.")
        except ImportError:
            print(f"Installing library '{dep}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ Library '{dep}' installed successfully!")
            except subprocess.CalledProcessError:
                print(f"❌ Error installing library '{dep}'. Please install it manually with 'pip install {dep}' and run the script again.")
                sys.exit(1)

install_dependencies()

# From this point on, libraries are guaranteed to be installed
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Initialize colorama for all systems
init(autoreset=True)

# Colors and styles to simulate an old green terminal
GREEN = Fore.GREEN
BLACK = Back.BLACK
RESET_ALL = Style.RESET_ALL

# Regular expression for URL validation
URL_PATTERN = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# --- Database and Script Logic Functions ---

def connect_db():
    """Connects to the database and creates the tables if they do not exist."""
    conn = sqlite3.connect('proposal_pilot.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            registration_date TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            project_name TEXT NOT NULL,
            project_description TEXT,
            proposal_value REAL,
            status INTEGER,
            proposal_link TEXT,
            questionnaire_link TEXT,
            contract_link TEXT,
            send_date TEXT,
            update_date TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS standard_replies (
            reply_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            subject TEXT,
            content TEXT
        )
    """)

    conn.commit()
    return conn, cursor

def is_valid_url(url):
    """Checks if a string is a valid URL."""
    if not url:
        return True
    return re.match(URL_PATTERN, url) is not None

def read_config():
    """Reads configurations from a JSON file."""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Saves configurations to a JSON file."""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def configure_email():
    """Guides the user to configure email credentials."""
    print(GREEN + "\n--- Email Configuration ---" + RESET_ALL)
    print(GREEN + "To send emails, we need some information." + RESET_ALL)
    print(GREEN + "If you use Gmail, you'll need an 'app password'. Learn how to generate one: https://bit.ly/3gY4jYk" + RESET_ALL)
    
    sender_email = input(GREEN + "Your email: " + RESET_ALL)
    password = input(GREEN + "Your app password: " + RESET_ALL)
    smtp_server = input(GREEN + "SMTP server (e.g., smtp.gmail.com): " + RESET_ALL)
    smtp_port = input(GREEN + "SMTP port (e.g., 587): " + RESET_ALL)

    config = {
        "sender_email": sender_email,
        "email_password": password,
        "smtp_server": smtp_server,
        "smtp_port": int(smtp_port)
    }

    save_config(config)
    print(GREEN + "✅ Email configuration saved successfully!" + RESET_ALL)

def send_email(recipient, subject, body):
    """Sends an email using the saved configurations."""
    config = read_config()
    if not config:
        print(GREEN + "❌ Error: Email configurations not found. Please configure them first." + RESET_ALL)
        return False
    
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config['sender_email']
        msg['To'] = recipient

        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['email_password'])
            server.send_message(msg)
        
        print(GREEN + f"✅ Email sent successfully to {recipient}!" + RESET_ALL)
        return True
    except Exception as e:
        print(GREEN + f"❌ Error sending email: {e}" + RESET_ALL)
        return False

def add_client(conn, cursor):
    """Prompts for client data and adds it to the database."""
    print(GREEN + "\n--- Register New Client ---")
    full_name = input(GREEN + "Full name: " + RESET_ALL)
    email = input(GREEN + "Email: " + RESET_ALL)
    phone = input(GREEN + "Phone: " + RESET_ALL)
    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute("INSERT INTO clients (full_name, email, phone, registration_date) VALUES (?, ?, ?, ?)",
                       (full_name, email, phone, registration_date))
        conn.commit()
        print(GREEN + f"✅ Client '{full_name}' registered successfully!" + RESET_ALL)
    except sqlite3.IntegrityError:
        print(GREEN + "❌ Error: This email is already registered." + RESET_ALL)

def add_proposal(conn, cursor):
    """Prompts for proposal data and adds it to the database, validating links."""
    print(GREEN + "\n--- Register New Proposal ---")
    try:
        client_id = int(input(GREEN + "Client ID: " + RESET_ALL))
        cursor.execute("SELECT client_id FROM clients WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            print(GREEN + "❌ Error: Client not found. Please register the client first." + RESET_ALL)
            return

        project_name = input(GREEN + "Project name: " + RESET_ALL)
        description = input(GREEN + "Project description: " + RESET_ALL)
        value = float(input(GREEN + "Proposal value: " + RESET_ALL))
        
        while True:
            proposal_link = input(GREEN + "Link to the proposal PDF: " + RESET_ALL)
            if is_valid_url(proposal_link): break
            print(GREEN + "❌ Invalid link. Please enter a full URL (e.g., https://...)" + RESET_ALL)
        
        while True:
            questionnaire_link = input(GREEN + "Link to the questionnaire (optional): " + RESET_ALL)
            if is_valid_url(questionnaire_link): break
            print(GREEN + "❌ Invalid link. Please enter a full URL (e.g., https://...)" + RESET_ALL)

        while True:
            contract_link = input(GREEN + "Link to the contract (optional): " + RESET_ALL)
            if is_valid_url(contract_link): break
            print(GREEN + "❌ Invalid link. Please enter a full URL (e.g., https://...)" + RESET_ALL)
        
        send_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 1 
        
        cursor.execute("""
            INSERT INTO proposals (client_id, project_name, project_description, proposal_value, status, proposal_link, questionnaire_link, contract_link, send_date, update_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (client_id, project_name, description, value, status, proposal_link, questionnaire_link, contract_link, send_date, send_date))
        conn.commit()
        print(GREEN + f"✅ Proposal for project '{project_name}' registered successfully!" + RESET_ALL)
    except ValueError:
        print(GREEN + "❌ Error: Client ID and proposal value must be numbers." + RESET_ALL)

def view_proposals(cursor):
    """Displays all proposals in a table format, with links."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(GREEN + "--- All Proposals ---" + RESET_ALL)
    cursor.execute("""
        SELECT p.proposal_id, c.full_name, p.project_name, p.proposal_value, p.status, p.update_date, p.proposal_link, p.questionnaire_link, p.contract_link
        FROM proposals p
        JOIN clients c ON p.client_id = c.client_id
        ORDER BY p.update_date DESC
    """)
    proposals = cursor.fetchall()
    
    if not proposals:
        print(GREEN + "No proposals found." + RESET_ALL)
        return

    headers = ["ID", "Client", "Project", "Value", "Status", "Update", "Links"]
    status_map = {1: "Sent", 2: "Negotiation", 3: "Accepted", 4: "Rejected"}
    table_data = []
    for prop in proposals:
        links_info = []
        if prop[6]: links_info.append("P")
        if prop[7]: links_info.append("Q")
        if prop[8]: links_info.append("C")
        
        prop_list = [
            prop[0],
            prop[1],
            prop[2],
            f"$ {prop[3]:.2f}",
            status_map.get(prop[4], "Unknown"),
            prop[5],
            ", ".join(links_info)
        ]
        table_data.append(prop_list)

    print(GREEN + tabulate(table_data, headers=headers, tablefmt="grid") + RESET_ALL)
    print(GREEN + "\nLink Legend: P=Proposal, Q=Questionnaire, C=Contract" + RESET_ALL)
    input(GREEN + "\nPress Enter to return to the menu..." + RESET_ALL)

def search_data(cursor):
    """Allows searching for clients or proposals by name."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(GREEN + "--- Search Clients/Proposals ---" + RESET_ALL)
    term = input(GREEN + "Enter search term (client or project name): " + RESET_ALL)
    term = f"%{term}%"

    print(GREEN + "\nClient Results:" + RESET_ALL)
    cursor.execute("SELECT client_id, full_name, email, phone FROM clients WHERE full_name LIKE ?", (term,))
    clients = cursor.fetchall()
    if clients:
        print(GREEN + tabulate(clients, headers=["ID", "Name", "Email", "Phone"], tablefmt="grid") + RESET_ALL)
    else:
        print(GREEN + "No clients found." + RESET_ALL)

    print(GREEN + "\nProposal Results:" + RESET_ALL)
    cursor.execute("""
        SELECT p.proposal_id, c.full_name, p.project_name, p.proposal_value
        FROM proposals p
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.project_name LIKE ? OR c.full_name LIKE ?
    """, (term, term))
    proposals = cursor.fetchall()
    if proposals:
        print(GREEN + tabulate(proposals, headers=["ID", "Client", "Project", "Value"], tablefmt="grid") + RESET_ALL)
    else:
        print(GREEN + "No proposals found." + RESET_ALL)

    input(GREEN + "\nPress Enter to return to the menu..." + RESET_ALL)

def update_proposal_status(conn, cursor):
    """Allows updating the status of a proposal."""
    print(GREEN + "\n--- Update Proposal Status ---" + RESET_ALL)
    try:
        proposal_id = int(input(GREEN + "ID of the proposal to be updated: " + RESET_ALL))
        cursor.execute("SELECT status FROM proposals WHERE proposal_id = ?", (proposal_id,))
        if not cursor.fetchone():
            print(GREEN + "❌ Error: Proposal not found." + RESET_ALL)
            return

        print(GREEN + "\nChoose the new status:" + RESET_ALL)
        print(GREEN + "1 - Sent" + RESET_ALL)
        print(GREEN + "2 - Negotiation" + RESET_ALL)
        print(GREEN + "3 - Accepted" + RESET_ALL)
        print(GREEN + "4 - Rejected" + RESET_ALL)
        new_status = int(input(GREEN + "New status (1-4): " + RESET_ALL))

        if new_status not in [1, 2, 3, 4]:
            print(GREEN + "❌ Error: Invalid status option." + RESET_ALL)
            return
        
        update_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE proposals SET status = ?, update_date = ? WHERE proposal_id = ?",
                       (new_status, update_date, proposal_id))
        conn.commit()
        print(GREEN + f"✅ Status of proposal {proposal_id} updated successfully!" + RESET_ALL)
    except ValueError:
        print(GREEN + "❌ Error: ID and status must be numbers." + RESET_ALL)

def generate_report(cursor):
    """Generates a performance report based on proposals."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(GREEN + "--- Performance Report ---" + RESET_ALL)
    
    cursor.execute("SELECT COUNT(*) FROM proposals")
    total_proposals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM proposals WHERE status = 3")
    accepted_proposals = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(proposal_value) FROM proposals WHERE status = 3")
    total_accepted_value = cursor.fetchone()[0] or 0.0

    acceptance_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0
    average_value = (total_accepted_value / accepted_proposals) if accepted_proposals > 0 else 0

    report_data = [
        ["Total Proposals", total_proposals],
        ["Accepted Proposals", accepted_proposals],
        ["Acceptance Rate", f"{acceptance_rate:.2f}%"],
        ["Total Value of Accepted", f"$ {total_accepted_value:.2f}"],
        ["Average Value per Project", f"$ {average_value:.2f}"]
    ]
    
    print(GREEN + tabulate(report_data, headers=["Metric", "Value"], tablefmt="grid") + RESET_ALL)
    input(GREEN + "\nPress Enter to return to the menu..." + RESET_ALL)

def edit_client(conn, cursor):
    """Edits data of an existing client."""
    print(GREEN + "\n--- Edit Client ---" + RESET_ALL)
    try:
        client_id = int(input(GREEN + "ID of the client to be edited: " + RESET_ALL))
        cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
        client = cursor.fetchone()
        if not client:
            print(GREEN + "❌ Error: Client not found." + RESET_ALL)
            return

        print(GREEN + f"\nSelected client: {client[1]}" + RESET_ALL)
        print(GREEN + "Which field do you want to edit?" + RESET_ALL)
        print(GREEN + "[1] Name" + RESET_ALL)
        print(GREEN + "[2] Email" + RESET_ALL)
        print(GREEN + "[3] Phone" + RESET_ALL)
        field_choice = input(GREEN + "Choose an option: " + RESET_ALL)

        if field_choice == '1':
            new_value = input(GREEN + "New full name: " + RESET_ALL)
            cursor.execute("UPDATE clients SET full_name = ? WHERE client_id = ?", (new_value, client_id))
        elif field_choice == '2':
            new_value = input(GREEN + "New email: " + RESET_ALL)
            cursor.execute("UPDATE clients SET email = ? WHERE client_id = ?", (new_value, client_id))
        elif field_choice == '3':
            new_value = input(GREEN + "New phone: " + RESET_ALL)
            cursor.execute("UPDATE clients SET phone = ? WHERE client_id = ?", (new_value, client_id))
        else:
            print(GREEN + "❌ Invalid option." + RESET_ALL)
            return

        conn.commit()
        print(GREEN + "✅ Client updated successfully!" + RESET_ALL)
    except ValueError:
        print(GREEN + "❌ Error: Client ID must be a number." + RESET_ALL)

def edit_proposal(conn, cursor):
    """Edits data of an existing proposal."""
    print(GREEN + "\n--- Edit Proposal ---" + RESET_ALL)
    try:
        proposal_id = int(input(GREEN + "ID of the proposal to be edited: " + RESET_ALL))
        cursor.execute("SELECT * FROM proposals WHERE proposal_id = ?", (proposal_id,))
        proposal = cursor.fetchone()
        if not proposal:
            print(GREEN + "❌ Error: Proposal not found." + RESET_ALL)
            return

        print(GREEN + f"\nSelected proposal: {proposal[2]}" + RESET_ALL)
        print(GREEN + "Which field do you want to edit?" + RESET_ALL)
        print(GREEN + "[1] Project Name" + RESET_ALL)
        print(GREEN + "[2] Description" + RESET_ALL)
        print(GREEN + "[3] Value" + RESET_ALL)
        print(GREEN + "[4] Proposal Link" + RESET_ALL)
        print(GREEN + "[5] Questionnaire Link" + RESET_ALL)
        print(GREEN + "[6] Contract Link" + RESET_ALL)
        field_choice = input(GREEN + "Choose an option: " + RESET_ALL)

        new_value = ""
        if field_choice == '1':
            new_value = input(GREEN + "New project name: " + RESET_ALL)
            cursor.execute("UPDATE proposals SET project_name = ? WHERE proposal_id = ?", (new_value, proposal_id))
        elif field_choice == '2':
            new_value = input(GREEN + "New description: " + RESET_ALL)
            cursor.execute("UPDATE proposals SET project_description = ? WHERE proposal_id = ?", (new_value, proposal_id))
        elif field_choice == '3':
            new_value = float(input(GREEN + "New value: " + RESET_ALL))
            cursor.execute("UPDATE proposals SET proposal_value = ? WHERE proposal_id = ?", (new_value, proposal_id))
        elif field_choice == '4':
            while True:
                new_value = input(GREEN + "New proposal link: " + RESET_ALL)
                if is_valid_url(new_value): break
                print(GREEN + "❌ Invalid link. Please enter a full URL." + RESET_ALL)
            cursor.execute("UPDATE proposals SET proposal_link = ? WHERE proposal_id = ?", (new_value, proposal_id))
        elif field_choice == '5':
            while True:
                new_value = input(GREEN + "New questionnaire link: " + RESET_ALL)
                if is_valid_url(new_value): break
                print(GREEN + "❌ Invalid link. Please enter a full URL." + RESET_ALL)
            cursor.execute("UPDATE proposals SET questionnaire_link = ? WHERE proposal_id = ?", (new_value, proposal_id))
        elif field_choice == '6':
            while True:
                new_value = input(GREEN + "New contract link: " + RESET_ALL)
                if is_valid_url(new_value): break
                print(GREEN + "❌ Invalid link. Please enter a full URL." + RESET_ALL)
            cursor.execute("UPDATE proposals SET contract_link = ? WHERE proposal_id = ?", (new_value, proposal_id))
        else:
            print(GREEN + "❌ Invalid option." + RESET_ALL)
            return

        conn.commit()
        print(GREEN + "✅ Proposal updated successfully!" + RESET_ALL)
    except ValueError:
        print(GREEN + "❌ Error: Proposal ID and value must be numbers." + RESET_ALL)

def edit_menu(conn, cursor):
    """Sub-menu for data editing."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(GREEN + "--- Edit Menu ---" + RESET_ALL)
        print(GREEN + "[1] Edit Client" + RESET_ALL)
        print(GREEN + "[2] Edit Proposal" + RESET_ALL)
        print(GREEN + "[0] Back" + RESET_ALL)
        
        option = input(GREEN + "\nChoose an option: " + RESET_ALL)
        
        if option == '1':
            edit_client(conn, cursor)
        elif option == '2':
            edit_proposal(conn, cursor)
        elif option == '0':
            break
        else:
            print(GREEN + "❌ Invalid option." + RESET_ALL)
            
        input(GREEN + "\nPress Enter to continue..." + RESET_ALL)

def add_standard_reply(conn, cursor):
    """Adds a new standard reply template."""
    print(GREEN + "\n--- Add Standard Reply ---" + RESET_ALL)
    type_reply = input(GREEN + "Reply type (e.g., 'Proposal Sent'): " + RESET_ALL)
    subject = input(GREEN + "Subject (e.g., 'Your Proposal for [project_name]'): " + RESET_ALL)
    content = input(GREEN + "Full reply content: " + RESET_ALL)
    
    try:
        cursor.execute("INSERT INTO standard_replies (type, subject, content) VALUES (?, ?, ?)",
                       (type_reply, subject, content))
        conn.commit()
        print(GREEN + f"✅ Standard reply '{type_reply}' 