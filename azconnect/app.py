import typer
import click
from typing import List, Annotated, Optional
from enum import Enum
from rich.console import Console
from rich.table import Table
from azconnect.azure_cli import get_cluster_list, connect_to_cluster
from azconnect.cache import invalidate_cache


clusters = get_cluster_list()
cluster_options = typer.Argument(click_type=click.Choice(choices=[cluster['name'] for cluster in clusters]))
cluster_options_int = typer.Option(
    click_type=click.Choice([str(i) for i in range(0, len(clusters))]),
)

console = Console()
app = typer.Typer()

@app.command(name='refresh')
def refresh_clusters():
    global clusters
    
    invalidate_cache()
    clusters = get_cluster_list()
    list_clusters()

@app.command(name='list')
def list_clusters():
    """List all Azure Kubernetes clusters"""

    table = Table("Num","Cluster Name", "Resource Group", "Subscription")
    for i, cluster in enumerate(clusters):
        table.add_row(str(i),cluster['name'],cluster['resourceGroup'],cluster['subscriptionId'])
    console.print(table)

@app.command(name='connect')
def select_cluster(choice : Annotated[Optional[str], cluster_options]=None, c : Annotated[int, cluster_options_int] =0):
    """Select an Azure Kubernetes cluster and run Azure commands"""
    
    if choice:
        selected_cluster = next((cluster for cluster in clusters if cluster["name"] == choice), None)
    else:
        selected_cluster = clusters[int(c)]

    if selected_cluster:
        typer.echo(f"Selected cluster: {selected_cluster['name']}")
        connect_to_cluster(selected_cluster)


if __name__ == "__main__":
    app()