from typing import Dict
from enum import Enum

class ClusterType(str, Enum):
    AKS = 'aks'
    ARC = 'arc-enabled'

class Subscription(Dict):
    def __init__(self, name: str, id: str):
        super().__init__()
        self['name'] = name
        self['id'] = id



class Cluster(Dict):
    def __init__(self, name: str, resource_group: str, subscription: Subscription, type: ClusterType):
        super().__init__()
        self['name'] = name
        self['resourceGroup'] = resource_group
        self['subscription'] = subscription
        self['type'] = type