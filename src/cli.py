import json
from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)

default_settings = {
    "ip": "192.168.0.1",
    "device": "RS_FSV",
    "overwrite_local_settings_state": True,
    "sweep_points": 1001,
    "average_state": False,
    "number_of_averages": 10,
    "freq_start": 1e6,
    "freq_stop": 1e6,
    "resolution_bw": 1e3,
}

current_settings = default_settings.copy()


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
