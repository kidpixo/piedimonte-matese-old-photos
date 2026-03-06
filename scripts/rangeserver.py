#!/usr/bin/env python

import argparse
import logging
import os
from http.server import HTTPServer, test
from RangeHTTPServer import RangeRequestHandler

class CORSRangeRequestHandler(RangeRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    parser = argparse.ArgumentParser(description="Minimal HTTP server with Range and CORS support.")
    parser.add_argument("--port", type=int, default=44000, help="Port to serve on (default: 44000)")
    parser.add_argument("--path", type=str, default=".", help="Directory to serve (default: current directory)")
    parser.add_argument("--log", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log), format="%(levelname)s: %(message)s")
    os.chdir(args.path)
    logging.info(f"Serving {os.path.abspath(args.path)} on port {args.port}")
    try:
        test(CORSRangeRequestHandler, HTTPServer, port=args.port)
    except KeyboardInterrupt:
        logging.info("Server stopped by user.")

if __name__ == "__main__":
    main()