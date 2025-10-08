# ==========================================
# 🚀 run_full_app.py — Lancement du backend + ngrok
# ==========================================
import os
import time
import threading
import webbrowser
from pyngrok import ngrok, conf
import uvicorn

# --- CONFIGURATION ---
PORT = 8000
conf.get_default().authtoken = "33jNW8yPGnqe8vzRcWmf7AOLVB7_2DGNEEwm7zruvfRa8pKRT"

def start_backend():
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, log_level="info")

def main():
    print("🚀 Démarrage FastAPI + Ngrok ...")
    threading.Thread(target=start_backend, daemon=True).start()
    time.sleep(3)

    # Création du tunnel ngrok
    public_url = ngrok.connect(PORT, bind_tls=True).public_url
    print("\n==============================================")
    print(f"🌐 URL publique     : {public_url}")
    print(f"📘 Docs Swagger     : {public_url}/api/docs")
    print(f"🧠 Endpoint API     : {public_url}/api/predict")
    print("==============================================\n")

    # Ouvre automatiquement ton front (index.html à la racine)
    webbrowser.open(f"{public_url}/")
    print("✅ Front ouvert dans le navigateur. (Ctrl+C pour arrêter)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Fermeture du tunnel Ngrok...")
        ngrok.kill()

if __name__ == "__main__":
    main()
