<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=wave&color=0:1F4F4F,100:00CED1&height=120&section=header&text=PropPilot%20CLI&fontSize=40&animation=fadeIn" alt="PropPilot CLI">
</p>

<p align="center">
  <i>✨ A simple and powerful tool for the modern freelancer.</i>
</p>

---

<p align="center">
  <a href="#-about-the-project">About</a> |
  <a href="#-features">Features</a> |
  <a href="#-prerequisites">Prerequisites</a> |
  <a href="#-installation-and-execution">Installation</a> |
  <a href="#-initial-configuration">Configuration</a> |
  <a href="#-how-to-use">How to Use</a> |
  <a href="#-project-structure">Structure</a> |
  <a href="#-contributing">Contributing</a>
</p>

---

### 📖 About the Project

**PropPilot** is a comprehensive and lightweight Python script designed for freelancers and small agencies seeking a simple yet robust solution to manage their sales pipeline.

This project was born from the need to centralize client management, proposals, and communication, eliminating the reliance on complex spreadsheets or expensive software. With an intuitive command-line interface, this script automates repetitive tasks, offers full control over your business data, and lets you focus on what truly matters: closing deals and delivering projects.

---

### 🚀 Features

PropPilot is equipped with a complete set of tools to optimize your workflow:

-   **Client and Proposal Management**: Easily manage clients and proposals, linking them within the database.
-   **Robust Validation**: URL validation for proposals, questionnaires, and contract links, ensuring your information is always correct.
-   **Email Templates**: Create and manage email templates for sending messages, with automatic placeholder substitution (`[client_name]`, `[project_name]`).
-   **Integrated Email Sending**: Send emails directly from the terminal to your clients using the saved templates and your configured credentials.
-   **Performance Analytics**: Generate instant reports with key metrics like acceptance rate and total revenue to make strategic business decisions.
-   **CSV Export**: Export your client and proposal data to `.csv` files, compatible with any spreadsheet software.
-   **Decentralized Configuration**: Email credentials and other settings are stored in a `config.json` file, allowing you to configure the script without modifying the source code.
-   **Automated Installation**: The script handles its own dependencies, ensuring a seamless **plug-and-play** experience.

---

### 🛠️ Prerequisites

-   <img src="https://img.shields.io/badge/Python-3.6+-306998?style=flat&logo=python" alt="Python Icon"> **Python 3.6 or higher**

---

### 📦 Installation and Execution

The installation process is automated and extremely simple:

1.  **Download the `propPilot.py` file** and save it to a folder of your choice.
2.  Open your terminal or command prompt.
3.  Navigate to the folder where you saved the file.
4.  **Execute the script** with the command:
    ```bash
    python propPilot.py
    ```

> ⚙️ The script will automatically check for and install the necessary libraries (`colorama`, `tabulate`) on the first run.

---

### 🔑 Initial Configuration

On your first run, it's recommended to configure your email credentials. This is the only manual configuration step, and your data is stored securely.

1.  In the main menu, select option **`[8] Utilities and Settings`**.
2.  Then, choose option **`[1] Configure Email`**.
3.  Provide your email, app password, and SMTP server details.
    -   **For Gmail**: You'll need to generate an **App Password** to allow the script to access your account. [Learn how to create an App Password here](https://support.google.com/accounts/answer/185833).

This information will be stored in the **`config.json`** file. Remember to keep this file secure and private.

---

### ⚡ How to Use

The script operates through an intuitive, numbered terminal menu. Here is a typical workflow:

-   **Add a client:** `[1]`
-   **Create a new proposal:** `[2]`
-   **View all proposals:** `[3]`
-   **Manage email templates:** `[7]`
-   **Send an email with a template:** `[7] > [3]`
-   **Export data:** `[8] > [2]`

---

### 📂 Project Structure

-   `propPilot.py`: The main script containing all functionalities.
-   `gerenciador_propostas.db`: The SQLite database that stores all your data.
-   `config.json`: The configuration file for email credentials.
-   `clients.csv`: The export file for client data.
-   `proposals.csv`: The export file for proposal data.

---

### 🤝 Contributing

Contributions make this project even better! If you have an idea or find a bug, feel free to:

1.  **Open an `Issue`**: To report bugs or suggest new features.
2.  **Create a `Pull Request`**: To submit your improvements or code corrections.

Thank you for your collaboration!

---

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=your-username&show_icons=true&theme=radical" alt="GitHub Stats">
  <img src="https://streak-stats.demolab.com/?user=j-c-flstk-dev &theme=radical" alt="GitHub Streak">
</p>

<p align="center">
  <a href="https://github.com/j-c-flstk-dev"><img src="https://img.shields.io/badge/Developed%20with-❤️%20and%20Python-blueviolet?style=flat-square&logo=python&logoColor=white" alt="Made with Python"></a>
</p>
