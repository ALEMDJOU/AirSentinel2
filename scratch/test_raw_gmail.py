import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_raw_gmail():
    host = "smtp.gmail.com"
    port = 587
    user = "fofackhenri36@gmail.com"
    password = "nrcc emex nodh gfme"  # Nouveau mot de passe
    
    print(f"Tentative de connexion à {host}:{port} avec {user}...")
    
    try:
        msg = MIMEMultipart()
        msg["Subject"] = "Test SMTP AirSentinel (Raw)"
        msg["From"] = user
        msg["To"] = user
        msg.attach(MIMEText("Ceci est un test en ligne de commande.", "plain"))
        
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(1)
        server.starttls()
        print("Connexion TLS établie.")
        
        server.login(user, password)
        print("Authentification réussie !")
        
        server.sendmail(user, [user], msg.as_string())
        print("Email envoyé avec succès !")
        
        server.quit()
        return True
    except Exception as e:
        print(f"ERREUR : {e}")
        return False

if __name__ == "__main__":
    test_raw_gmail()
