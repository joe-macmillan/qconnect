import typer
import click
from typing import List, Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from azconnect.azure_cli import get_cluster_list, connect_to_cluster
from azconnect.cache import invalidate_cache


clusters = get_cluster_list()
cluster_name_argument = typer.Argument(click_type=click.Choice(choices=[cluster['name'] for cluster in clusters]))
cluster_options_int = typer.Option(
    click_type=click.Choice([str(i) for i in range(0, len(clusters))]),
)

console = Console()
app = typer.Typer()

@app.command(name='refresh')
def refresh_clusters():
    """Refresh list of Kubernetes clusters"""
    global clusters

    invalidate_cache()
    clusters = get_cluster_list()
    list_clusters()

@app.command(name='ls')
def list_clusters():
    """List available Kubernetes clusters"""

    table = Table("Index","Cluster Name", "Resource Group", "Subscription")
    for i, cluster in enumerate(clusters):
        table.add_row(str(i),cluster['name'],cluster['resourceGroup'],cluster['subscription']['name'])
    console.print(table)

@app.command(name='connect')
def select_cluster(choice : Annotated[Optional[str], cluster_name_argument]=None, c : Annotated[Optional[str], cluster_options_int] ='0'):
    """Select a Kubernetes cluster to connect to through Azure"""
    
    if choice:
        selected_cluster = next((cluster for cluster in clusters if cluster["name"] == choice), None)
    else:
        selected_cluster = clusters[int(c)]

    if selected_cluster:
        typer.echo(f"Selected cluster: {selected_cluster['name']}")
        connect_to_cluster(selected_cluster)


if __name__ == "__main__":
    app()