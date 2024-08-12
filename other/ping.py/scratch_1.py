import time
from ping3 import ping

def ping_host(host, timeout=10, interval=5):
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Versuche, den Host zu pingen
            result = ping(host)
            if result is not None:
                # Erfolgreiches Pingen, gibt True zurück
                return True
        except Exception:
            # Bei einem Fehler warte für das angegebene Intervall
            time.sleep(interval)

    # Zeitüberschreitung, gibt False zurück
    return False

# Beispielaufruf
host_to_ping = "192.168.8.2"
result = ping_host(host_to_ping)

if result:
    print(f"Der Host {host_to_ping} ist erreichbar.")
else:
    print(f"Der Host {host_to_ping} konnte nicht erreicht werden.")
