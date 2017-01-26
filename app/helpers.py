# Standard Lib imports
import os
# Third-party imports
# BITSON imports


def create_folders(app):
    """Creates folder structure and every config variable ending with
    '_FOLDER'. """
    for k, v in app.config.items():
        if '_FOLDER' in k:
            if os.path.isdir(v):
                continue
            else:
                os.mkdir(v)


def register_blueprints(app, blueprints, url_prefix=None):
    for blueprint in blueprints:
        app.register_blueprint(blueprint,
                               url_prefix=url_prefix or blueprint.url_prefix)


def register_apis(apimanager, apis, url_prefix):
    for api in apis:
        apimanager.create_api(api, methods=api.methods, url_prefix=url_prefix,
                              preprocessors=api.preprocessors,
                              postprocessors=api.postprocessors,
                              results_per_page=api.results_per_page,
                              max_results_per_page=api.max_results_per_page,
                              include_methods=api.include_methods,
                              validation_exceptions=api.validation_exceptions,
                              include_columns=api.include_columns,
                              exclude_columns=api.exclude_columns,
                              )
