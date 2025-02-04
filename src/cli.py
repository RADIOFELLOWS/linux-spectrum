import json
import logging
from typing import Annotated

import pyvisa
import typer

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
app = typer.Typer(no_args_is_help=True)

json_file_path = "default_settings.json"
with open(json_file_path, "r") as json_file:
    default_settings = json.load(json_file)
current_settings = default_settings.copy()


@app.command()
def send_command():
    rm = pyvisa.ResourceManager("@py")
    rm.list_resources()


@app.command()
def get_trace():
    """
    Get the trace of from the spectrum analyzer (prints to terminal and stdout)
    """
    pass


@app.command()
def settings(
    settings: Annotated[
        str,
        typer.Argument(help="JSON string representing settings to override defaults."),
    ] = "",
):
    """
    Main command that optionally updates current settings from a JSON string.
    """
    if settings:
        try:
            new_settings = json.loads(settings)
            # Update current settings with any new keys/values
            current_settings.update(new_settings)
        except json.JSONDecodeError:
            typer.echo("Invalid JSON format. No updates applied.")
            raise typer.Exit(code=1)

    # Display current settings
    typer.echo("Current settings:")
    typer.echo(json.dumps(current_settings, indent=2))
    return current_settings


@app.command()
def set_ip(ip: Annotated[str, typer.Argument(help="New IP address to set.")]):
    """
    Command to set the IP address for the Spectrum Analyzer you would like to
    use.
    """
    current_settings["ip"] = ip
    typer.echo(f"IP updated to: {ip}")
    return ip


if __name__ == "__main__":
    app()
