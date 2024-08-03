def register_resources(app, api, resources, prefix=None):
    """
      Assign api resources to given
      flask restful instance
    """
    app.logger.info(
        "Registering resource modules{}...".format(prefix))
    for resource in resources:
        if resource is not None:
            # Set base rule and disable prefix to false
            rule = resource['rule']
            disable_prefix = False

            # Detect if resource passing disable_prefix in options
            if 'disable_prefix' in resource:
                disable_prefix = resource['disable_prefix']

            # Set prefix if prefix is passed and disable_prefix options
            # are not true
            if prefix is not None and not disable_prefix:
                rule = "{}{}".format(prefix, rule,)

            # Add resource to API Blueprint
            api.add_resource(
                resource['resource_class'],
                rule
            )
