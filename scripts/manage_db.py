#!/usr/bin/env python3
import os
import argparse
from alembic.config import Config
from alembic import command

def run_migrations(args):
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    if args.command == "upgrade":
        command.upgrade(alembic_cfg, "head")
    elif args.command == "downgrade":
        command.downgrade(alembic_cfg, "-1")
    elif args.command == "revision":
        command.revision(alembic_cfg, autogenerate=True, message=args.message)
    elif args.command == "history":
        command.history(alembic_cfg)
    elif args.command == "current":
        command.current(alembic_cfg)

def main():
    parser = argparse.ArgumentParser(description="Database migration manager")
    parser.add_argument(
        "command",
        choices=["upgrade", "downgrade", "revision", "history", "current"],
        help="Migration command to execute"
    )
    parser.add_argument(
        "--message",
        help="Migration message (required for 'revision' command)",
        default=None
    )
    
    args = parser.parse_args()
    run_migrations(args)

if __name__ == "__main__":
    main()
