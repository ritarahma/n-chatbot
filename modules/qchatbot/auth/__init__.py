from .resources import AuthenticationResources

resources = (
    dict(
        rule="/",
        resource_class=AuthenticationResources,
    ),

)
