from apscheduler.schedulers.background import BackgroundScheduler
import requests

def mantener_vivo():
    try:
        url = "https://pruebas1-d2o0.onrender.com/"  # Reemplaza con tu URL real
        requests.get(url)  # Hace una solicitud GET para evitar que se duerma
        #print("✔ Backend despertado exitosamente.")
    except Exception as e:
        pass
        #print("❌ Error al hacer ping al backend:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(mantener_vivo, "interval", minutes=10)  # Ejecuta cada 5 minutos
scheduler.start()