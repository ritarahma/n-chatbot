from .views import Root

resources = (
    dict(
        rule="/",
        resource_class=Root,
        disable_prefix=True,
    ),
)
