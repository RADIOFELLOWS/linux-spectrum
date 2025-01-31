from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def set_ip(ip: Annotated[str, typer.Option()]):
    print(ip)
