#!/usr/bin/env python3
<<<<<<< HEAD:exporter.py
# -*- encoding: utf-8 -*-

"""
Python exporter for active user sessions scraped from the `who` CLI output
"""

=======

import sys
>>>>>>> compose:exporter/exporter.py
import argparse
import logging
import subprocess
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import Gauge, generate_latest, CollectorRegistry


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=sys.stderr)

collector = CollectorRegistry()

who_up = Gauge("who_up", "Status of the exporter", registry=collector)
who_active = Gauge("who_active", "Number of active sessions per user", ["username"], registry=collector)


def get_active_sessions() -> dict[str, int]:
    """
    Scrape user sessions from /var/run/utmp via `who`.

    :return: Dictionary of session counts per user
    """
    try:
        result = subprocess.run(["who", "-u", "/var/run/utmp"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logging.error("Failed to run `who`: '%s'", result.stderr)
            return {}

        sessions: dict[str, int] = {}
        for line in result.stdout.splitlines():
            username = line.split()[0]
            sessions[username] = sessions.get(username, 0) + 1

        return sessions
    except Exception as e:
        logging.error("Error getting active sessions: %s", e)
        return {}


class MetricsHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for Prometheus metrics.
    """
    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """
        Handle HTTP GET requests.
        """
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
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error generating metrics: %s", e)
                self.send_error(500)
        else:
            self.send_error(404)


def run_exporter(port: int) -> None:
    """
    Run a Prometheus exporter on the specified port.
    """
    server_address = ("", port)
    httpd = HTTPServer(server_address, MetricsHandler)
    logging.info("Starting exporter on port %s...", port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping exporter...")
    finally:
        httpd.server_close()
        logging.info("Exporter stopped.")


def main() -> None:
    """
    Parse command-line arguments and start the Prometheus exporter.
    """
    parser = argparse.ArgumentParser(description="Prometheus exporter for active user sessions.")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to expose metrics on (default: 8000)")
    args = parser.parse_args()

    run_exporter(args.port)


if __name__ == "__main__":
    main()
