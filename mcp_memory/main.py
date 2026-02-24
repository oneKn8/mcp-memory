import click


@click.group()
@click.version_option()
def cli():
    """MCP server for persistent agent memory with semantic search"""
    pass


@cli.command()
def hello():
    """Say hello."""
    click.echo("Hello from mcp-memory!")


if __name__ == "__main__":
    cli()
