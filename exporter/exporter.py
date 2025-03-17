#!/usr/bin/env python3

import sys
import argparse
import logging
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import Gauge, generate_latest,CollectorRegistry 

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",stream=sys.stderr)

collector=CollectorRegistry()

who_up = Gauge("who_up", "Status of the exporter",registry=collector)
who_active = Gauge("who_active", "Number of active sessions per user", ["username"],registry=collector)


def get_active_sessions():
    try:
        result = subprocess.run(["who", "-u", "/var/run/utmp"], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Failed to run 'who': {result.stderr}")
            return {}

        sessions = {}
        for line in result.stdout.splitlines():
            username = line.split()[0]
            sessions[username] = sessions.get(username, 0) + 1

        return sessions
    except Exception as e:
        logging.error(f"Error getting active sessions: {e}")
        return {}


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            try:
                who_up.set(1) 

                active_sessions = get_active_sessions()
                for username, count in active_sessions.items():
                    who_active.labels(username=username).set(count)

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(generate_latest(collector))
            except Exception as e:
                logging.error(f"Error generating metrics: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")


def run_exporter(port):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MetricsHandler)
    logging.info(f"Starting exporter on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping exporter...")
    finally:
        httpd.server_close()
        logging.info("Exporter stopped.")


def main():
    parser = argparse.ArgumentParser(description="Prometheus exporter for active user sessions.")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to expose metrics on (default: 8000)")
    args = parser.parse_args()

    run_exporter(args.port)
    

if __name__ == "__main__":
    main()
