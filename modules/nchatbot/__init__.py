from .resources import ModelResources
from .resources import PrepResources
from .template_resources import templateResources
from .chatInterface_resources import chatInterfaceResources

resources = (
    dict(
        rule="/train",
        resource_class=ModelResources,
    ),
    dict(
        rule="/train/prep/lemma",
        resource_class=PrepResources,
    ),
    dict(
        rule="/template",
        resource_class=templateResources,
    ),
    dict(
        rule="/chat",
        resource_class=chatInterfaceResources,
    ),
)
