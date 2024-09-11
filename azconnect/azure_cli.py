from azure.cli.core import get_default_cli
from azconnect.cache import load_cache, save_cache, CacheType
from azconnect.models import Cluster, ClusterType

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


def get_cluster_list()-> list[Cluster]:
    
    cached_clusters = load_cache(CacheType.CLUSTER)
    if cached_clusters:
        return cached_clusters
            

    subscriptions = get_subscription_list()

    cli = get_default_cli()
    aks_clusters = []
    arc_clusters = []
    for sub in subscriptions:
        cli.invoke(['account', 'set', '--subscription', sub ,"--output", "none" ])
        cli.invoke(["aks", "list", "--output", "none"])
        result = cli.result.result
        for aks in result:
            aks_clusters.append(
                Cluster(
                name=aks.get('name'),
                resource_group=aks.get('resourceGroup'),
                subscription_id=sub,
                type=ClusterType.AKS
                )
            )
        
        cli.invoke(["connectedk8s", "list", "--output", "none"])
        result = cli.result.result
        for arc in result:
            arc_clusters.append(
                Cluster(
                name=arc.get('name'),
                resource_group=arc.get('resourceGroup'),
                subscription_id=sub,
                type=ClusterType.ARC
                )
            )
    
    all_clusters = [*aks_clusters, *arc_clusters]
    save_cache(CacheType.CLUSTER,data=all_clusters)

    return all_clusters

def connect_to_cluster(cluster: Cluster):
    cli = get_default_cli()
    cli.invoke(['account', 'set', '--subscription', cluster['subscriptionId'] ,"--output", "none" ])

    if cluster['type'] == ClusterType.AKS:
        cli.invoke(["aks", "get-credentials", "--name", cluster['name'], "--resource-group", cluster['resourceGroup']])
    elif cluster['type'] == ClusterType.ARC:
        cli.invoke(['connectedk8s', 'proxy',"--name", cluster['name'], "--resource-group", cluster['resourceGroup']])
