from typing import Dict
from enum import Enum

class ClusterType(str, Enum):
    AKS = 'aks'
    ARC = 'arc-enabled'


class Cluster(Dict):
    def __init__(self, name: str, resource_group: str, subscription_id: str, type: ClusterType):
        super().__init__()
        self['name'] = name
        self['resourceGroup'] = resource_group
        self['subscriptionId'] = subscription_id
        self['type'] = type