import typer
import click
from typing import List, Annotated, Optional
from azure.cli.core import get_default_cli
import json
import os
import time
from enum import Enum
from rich.console import Console
from rich.table import Table
from pathlib import Path



class CacheType(str, Enum):
    CLUSTER = 'cluster'
    SUBSCRIPTION = 'subs'

DATA_FOLDER = Path.home() /'.qc/'
Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)
CLUSTER_CACHE_FILE = DATA_FOLDER / "clusters.json"
SUBSCRIPTION_CACHE_FILE = DATA_FOLDER / "subscriptions.json"
CACHE_TIMEOUT = 24 * 60 * 60  # 24 Hours

def invalidate_cache():
    if os.path.exists(CLUSTER_CACHE_FILE):
        os.remove(CLUSTER_CACHE_FILE)
    if os.path.exists(SUBSCRIPTION_CACHE_FILE):
        os.remove(SUBSCRIPTION_CACHE_FILE)

def load_cache(what: CacheType):
    """Loads cached data if available and valid."""
    cache_file = CLUSTER_CACHE_FILE if what == CacheType.CLUSTER else SUBSCRIPTION_CACHE_FILE
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
                if time.time() - cache_data["timestamp"] < CACHE_TIMEOUT:
                    return cache_data[what]
        except (json.JSONDecodeError, KeyError):
            pass  # Ignore and rebuild cache
    return None

def save_cache(what: CacheType, data: list):
    """Saves data to cache."""
    cache_file = CLUSTER_CACHE_FILE if what == CacheType.CLUSTER else SUBSCRIPTION_CACHE_FILE
    with open(cache_file, "w") as f:
        json.dump({"timestamp": time.time(), what: data}, f)


def get_subscription_list():
    cached_subs = load_cache(CacheType.SUBSCRIPTION)
    if cached_subs:
        return cached_subs
    cli = get_default_cli()
    cli.invoke(['account', 'subscription', 'list',"--output", "none" ])
    result = cli.result.result
    subscriptions = [sub.get('subscriptionId') for sub in result]
    save_cache(CacheType.SUBSCRIPTION,data=subscriptions)

    return subscriptions


def get_cluster_list():
    
    cached_clusters = load_cache(CacheType.CLUSTER)
    if cached_clusters:
        return cached_clusters
            

    subscriptions = get_subscription_list()

    cli = get_default_cli()
    aks_clusters = []
    quasar_clusters = []
    for sub in subscriptions:
        cli.invoke(['account', 'set', '--subscription', sub ,"--output", "none" ])
        cli.invoke(["aks", "list", "--output", "none"])
        result = cli.result.result
        for aks in result:
            aks_clusters.append({
                "name": aks.get('name'),
                "resourceGroup": aks.get('resourceGroup'),
                "subscriptionId": sub,
                "type": 'aks'
            })
        
        cli.invoke(["connectedk8s", "list", "--output", "none"])
        result = cli.result.result
        for quasar in result:
            quasar_clusters.append(
                {
                "name": quasar.get('name'),
                "resourceGroup": quasar.get('resourceGroup'),
                "subscriptionId": sub,
                "type": 'quasar'
            }
            )
    
    all_clusters = [*aks_clusters, *quasar_clusters]
    save_cache(CacheType.CLUSTER,data=all_clusters)

    return all_clusters

def connect_to_cluster(cluster: dict):
    cli = get_default_cli()
    cli.invoke(['account', 'set', '--subscription', cluster['subscriptionId'] ,"--output", "none" ])

    if cluster['type'] == "aks":
        cli.invoke(["aks", "get-credentials", "--name", cluster['name'], "--resource-group", cluster['resourceGroup']])
    elif cluster['type'] == "quasar":
        cli.invoke(['connectedk8s', 'proxy',"--name", cluster['name'], "--resource-group", cluster['resourceGroup']])



clusters = get_cluster_list()
cluster_options = typer.Argument(click_type=click.Choice(choices=[cluster['name'] for cluster in clusters]))
cluster_options_int = typer.Option(
    click_type=click.Choice([str(i) for i in range(0, len(clusters))]),
)

console = Console()
app = typer.Typer()

@app.command(name='refresh')
def refresh_clusters():
    invalidate_cache()
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