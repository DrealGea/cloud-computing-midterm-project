
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, parse_qs

PORT = int(os.getenv("PORT", "5000"))
DATA_FILE = Path(os.getenv("DATA_FILE", "data/guestbook.json"))
LOCK = Lock()


# Membaca data tamu dari file JSON
def load_data():
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Format penyimpanan tidak valid")

    return data


# Menyimpan data tamu ke file JSON
def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = DATA_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    os.replace(temp_file, DATA_FILE)


class GuestbookAPI(BaseHTTPRequestHandler):

    # Mengirim respons JSON
    def send_json(self, status, data):
        response = json.dumps(
            data, ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type", "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, DELETE, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()
        self.wfile.write(response)

    # Menangani CORS preflight
    def do_OPTIONS(self):
        self.send_json(200, {"status": "ok"})

    # GET: Menampilkan daftar tamu
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/health":
            self.send_json(200, {
                "status": "active",
                "service": "Guestbook API"
            })
            return

        if path == "/messages":
            try:
                with LOCK:
                    data = load_data()

                self.send_json(200, {"data": data})

            except (OSError, ValueError):
                self.send_json(500, {
                    "error": "Gagal membaca data tamu"
                })
            return

        self.send_json(404, {
            "error": "Endpoint tidak ditemukan"
        })

    # POST: Menambahkan tamu
    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/messages":
            self.send_json(404, {
                "error": "Endpoint tidak ditemukan"
            })
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 10000:
                raise ValueError("Ukuran data tidak valid")

            body = json.loads(
                self.rfile.read(length).decode("utf-8")
            )

            if not isinstance(body, dict):
                raise ValueError("JSON harus berupa objek")

        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {
                "error": "Format JSON tidak valid"
            })
            return

        name = body.get("name")
        message = body.get("message")

        if not isinstance(name, str) or not name.strip():
            self.send_json(400, {
                "error": "Nama tamu wajib diisi"
            })
            return

        if not isinstance(message, str) or not message.strip():
            self.send_json(400, {
                "error": "Pesan wajib diisi"
            })
            return

        if len(name) > 100 or len(message) > 500:
            self.send_json(400, {
                "error": "Data melebihi batas karakter"
            })
            return

        guest = {
            "name": name.strip(),
            "message": message.strip(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            with LOCK:
                data = load_data()
                data.append(guest)
                save_data(data)

        except (OSError, ValueError):
            self.send_json(500, {
                "error": "Gagal menyimpan data tamu"
            })
            return

        self.send_json(201, {
            "message": "Tamu berhasil ditambahkan",
            "data": guest
        })

    # DELETE: Menghapus tamu berdasarkan index
    def do_DELETE(self):
        parsed = urlparse(self.path)

        if parsed.path != "/messages":
            self.send_json(404, {
                "error": "Endpoint tidak ditemukan"
            })
            return

        params = parse_qs(parsed.query)

        try:
            index = int(params.get("index", [None])[0])
        except (TypeError, ValueError):
            self.send_json(400, {
                "error": "Index tidak valid"
            })
            return

        if index < 0:
            self.send_json(400, {
                "error": "Index tidak valid"
            })
            return

        try:
            with LOCK:
                data = load_data()

                if index >= len(data):
                    self.send_json(404, {
                        "error": "Data tamu tidak ditemukan"
                    })
                    return

                deleted = data.pop(index)
                save_data(data)

        except (OSError, ValueError):
            self.send_json(500, {
                "error": "Gagal menghapus data tamu"
            })
            return

        self.send_json(200, {
            "message": "Tamu berhasil dihapus",
            "data": deleted
        })


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        GuestbookAPI
    )

    print(f"Backend berjalan pada port {PORT}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
