"""
qB-QueueMETA.py

This script connects to a qBittorrent instance via its Web API and monitors torrents.
Torrents that do not have metadata (has_metadata is False) will be force-started.
Once metadata is retrieved, the torrent will be returned to its regular downloading state.

The intent for this script is to ensure that all queued torrents are briefly allowed to
bypass the maximum active downloads rule, grab their metadata, then be returned to the queue.

Settings can be provided via a YAML configuration file using the --config argument.
Any command-line options will override config file values.

Usage example:
    python qB-QueueMETA.py --config config.yaml --host localhost:8080 \
       --username admin --password adminadmin --interval 60 [--once] [--verbose] [--no-verify-certificate]

YAML config file example (config.yaml):
    host: "localhost:8080"
    username: "admin"
    password: "adminadmin"
    interval: 60
    once: false
    verbose: false
    verify_certificate: true
"""

import argparse
import logging
import sys
import time
import os

try:
    import qbittorrentapi
except ImportError:
    sys.exit("Error: qbittorrentapi module not found. Install it with 'pip install qbittorrent-api'.")

try:
    import yaml
except ImportError:
    sys.exit("Error: PyYAML module not found. Install it with 'pip install PyYAML'.")


def load_config_file(config_path: str) -> dict:
    """
    Load configuration settings from a YAML file.
    """
    if not os.path.isfile(config_path):
        logging.error(f"Config file '{config_path}' does not exist.")
        return {}
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            if config is None:
                return {}
            return config
    except Exception as e:
        logging.exception(f"Failed to load config file '{config_path}'")
        return {}


def parse_args():
    # First, parse only the --config argument to find the config file
    initial_parser = argparse.ArgumentParser(add_help=False)
    initial_parser.add_argument("--config", type=str, help="Path to YAML configuration file")
    initial_args, remaining_argv = initial_parser.parse_known_args()

    config = {}
    if initial_args.config:
        config = load_config_file(initial_args.config)

    # Now parse all arguments, using the config for defaults
    parser = argparse.ArgumentParser(
        description="Monitor and force-start torrents in qBittorrent waiting for metadata, and revert them to normal state once metadata is retrieved."
    )
    # Add all arguments, using config values as defaults
    parser.add_argument("--config", type=str, help="Path to YAML configuration file")
    parser.add_argument("--host", help="qBittorrent Web UI URL (e.g., localhost:8080)", default=config.get("host"))
    parser.add_argument("--username", help="qBittorrent username (if needed)", default=config.get("username", ""))
    parser.add_argument("--password", help="qBittorrent password (if needed)", default=config.get("password", ""))
    parser.add_argument("--interval", type=int, default=config.get("interval", 60),
                        help="Polling interval in seconds (default: %(default)s)")
    parser.add_argument("--once", action="store_true", default=config.get("once", False),
                        help="Run once and exit")
    parser.add_argument("--verbose", action="store_true", default=config.get("verbose", False),
                        help="Enable debug logging")
    # Handle verify_certificate with mutual exclusion
    verify_cert_default = config.get("verify_certificate", True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verify-certificate", dest="verify_certificate", action="store_true",
                       help="Verify Web UI certificate (default)" if verify_cert_default else "Verify Web UI certificate")
    group.add_argument("--no-verify-certificate", dest="verify_certificate", action="store_false",
                       help="Do not verify Web UI certificate")
    parser.set_defaults(verify_certificate=verify_cert_default)

    args = parser.parse_args(remaining_argv)
    return args


def process_torrents(qbt_client: qbittorrentapi.Client):
    """
    Iterate through all torrents:
      - If a torrent does not have metadata (has_metadata is False), force-start it.
      - If metadata is available and torrent is still forced, disable force-start.
    """
    try:
        torrents = qbt_client.torrents.info()
    except Exception as e:
        logging.exception("Error fetching torrents")
        return

    for torrent in torrents:
        has_metadata = getattr(torrent, "has_metadata", True)
        is_forced = getattr(torrent, "force_start", False)

        if not has_metadata:
            if not is_forced:
                try:
                    qbt_client.torrents.set_force_start(torrent_hashes=[torrent.hash], enable=True)
                    logging.info(f"Force-started torrent '{torrent.name}' (hash: {torrent.hash}) for metadata retrieval")
                except Exception as e:
                    logging.exception(f"Failed to force start torrent '{torrent.name}' (hash: {torrent.hash})")
        elif has_metadata and is_forced:
            try:
                qbt_client.torrents.set_force_start(torrent_hashes=[torrent.hash], enable=False)
                logging.info(f"Disabled force-start for torrent '{torrent.name}' (hash: {torrent.hash}); metadata retrieved")
            except Exception as e:
                logging.exception(f"Failed to disable force start for torrent '{torrent.name}' (hash: {torrent.hash})")


def main():
    args = parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("Starting qB-Queueᴹᴱᵀᴬ script...")

    if not args.host:
        logging.error("qBittorrent host URL must be provided via --host or in the config file.")
        sys.exit(1)

    try:
        qbt_client = qbittorrentapi.Client(
            host=args.host,
            username=args.username,
            password=args.password,
            VERIFY_WEBUI_CERTIFICATE=args.verify_certificate
        )
        qbt_client.auth_log_in()
    except Exception as e:
        logging.exception("Error connecting to qBittorrent")
        sys.exit(1)

    if args.once:
        process_torrents(qbt_client)
    else:
        while True:
            process_torrents(qbt_client)
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
