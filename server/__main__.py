import sys
sys.path.append("server")

from fleetman_http_api.__main__ import main as run_server

if __name__ == '__main__':
    run_server()