import json
import logging
from contextlib import contextmanager
from typing import Annotated, Optional

import pyvisa
import typer
from rich.console import Console
from rich.table import Table

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
app = typer.Typer(no_args_is_help=True)

json_file_path = "default_settings.json"
with open(json_file_path, "r") as json_file:
    default_settings = json.load(json_file)
current_settings = default_settings.copy()


@contextmanager
def instrument_context(current_settings):
    """
    Context manager for handling the PyVISA Resource Manager and instrument connection.

    Args:
        current_settings (dict): The current settings containing the IP address of the instrument.

    Raises:
        RuntimeError: If the IP address is not set or if there is an error communicating with the instrument.
    """
    try:
        ip_address = current_settings.get("ip")
        if not ip_address:
            raise RuntimeError("IP address not set in current settings.")

        rm = pyvisa.ResourceManager("@py")
        # Open a connection to the instrument
        instrument = rm.open_resource(f"TCPIP::{ip_address}::INSTR", timeout=5000)
        yield instrument  # Yield the instrument for use in the context

    except RuntimeError as e:
        # Handle runtime errors related to IP address and other issues
        raise RuntimeError(f"Runtime error: {e}")
    except pyvisa.VisaIOError as e:
        # Handle VISA communication errors
        raise RuntimeError(f"Error communicating with the spectrum analyzer: {e}")
    except Exception as e:
        # Handle any other unexpected errors
        raise RuntimeError(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the instrument is closed properly
        try:
            instrument.close()
        except Exception as e:
            # Log or handle any errors that occur during closing
            print(f"Error closing the instrument: {e}")


@app.command()
def command(message: str):
    with instrument_context(current_settings) as instrument:
        resp = instrument.query(str(message))
        typer.echo(f"repsponse: \n{resp}")


@app.command()
def errorlog(truncate: Annotated[Optional[bool], typer.Option()] = True):
    with instrument_context(current_settings) as instrument:
        message_count = 0
        while True:
            error_message = instrument.query("SYST:ERR?").strip()
            message_count += 1
            typer.echo(error_message)
            if error_message.startswith("0"):
                break
            if truncate is False and (message_count >= 10):
                break


@app.command()
def ls():
    """
    List all connected instruments and retrieve their IDN.
    Args:
        current_settings (dict): The current settings containing the IP address of the instruments.
    """
    console = Console()
    temp_settings = current_settings.copy()
    try:
        rm = pyvisa.ResourceManager("@py")
        resources = rm.list_resources()

        if not resources:
            console.print("No instruments found.")
            return

        # Create a Rich Table
        table = Table(title="Connected Instruments")

        # Define the columns
        table.add_column("Resource", justify="left", style="cyan", no_wrap=True)
        table.add_column("IP Address", justify="left", style="magenta")
        table.add_column("Instrument ID", justify="left", style="green")

        for resource in resources:
            # Extract the IP address from the resource string if needed
            # Assuming the resource string is in the format "TCPIP::192.168.1.107::INSTR"
            ip_address = resource.split("::")[1]  # Extracting the IP address
            temp_settings["ip"] = ip_address

            with instrument_context(temp_settings) as instrument:
                idn = instrument.query("*IDN?")
                table.add_row(resource, ip_address, idn)

        console.print(table)

    except Exception as e:
        print(f"An error occurred while listing instruments: {e}")


@app.command()
def id():
    with instrument_context(current_settings) as instrument:
        idn = instrument.query("*IDN?")
        typer.echo(f"Instrument ID: {idn}")


@app.command()
def learn():
    with instrument_context(current_settings) as instrument:
        lrn = instrument.query("*LRN?")
        typer.echo(f"Instrument settings available: {lrn}")


@app.command()
def get_trace():
    """
    Get the trace of from the spectrum analyzer (prints to terminal and stdout)
    """

    with instrument_context(current_settings) as instrument:
        # Send command to get frequency and power data
        frequency_data = instrument.query(
            "FREQ:DATA?"
        )  # Example command to get frequency data
        power_data = instrument.query(
            "TRAC:DATA?"
        )  # Example command to get trace data (power)

        # Convert the received data into lists
        frequency_list = [float(f) for f in frequency_data.split(",")]
        power_list = [float(p) for p in power_data.split(",")]

        # Check if both lists have the same length
        if len(frequency_list) != len(power_list):
            typer.echo("Mismatch in frequency and power data lengths.")
            raise typer.Exit(code=1)

        # Print the data in CSV format
        typer.echo("Frequency (Hz), Power (dBm)")
        for freq, power in zip(frequency_list, power_list):
            typer.echo(f"{freq}, {power}")


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
