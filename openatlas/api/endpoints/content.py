from typing import Union

from flask import Response, g
from flask_restful import Resource, marshal

from openatlas import app
from openatlas.api.resources.model_mapper import get_overview_counts
from openatlas.api.resources.parser import language, default
from openatlas.api.resources.resolve_endpoints import download
from openatlas.api.resources.templates import (
    class_overview_template, content_template, overview_template,
    backend_details_template)
from openatlas.models.content import get_translation


class GetContent(Resource):
    @staticmethod
    def get() -> Union[tuple[Resource, int], Response]:
        parser = language.parse_args()
        lang = parser['lang']
        content = {
            'intro': get_translation('intro_for_frontend', lang),
            'contact': get_translation('contact_for_frontend', lang),
            'siteName': get_translation('site_name_for_frontend', lang),
            'imageSizes': app.config['IMAGE_SIZE'],
            'legalNotice': get_translation('legal_notice_for_frontend', lang)}
        if parser['download']:
            download(content, content_template(), 'content')
        return marshal(content, content_template()), 200


class GetBackendDetails(Resource):
    @staticmethod
    def get() -> Union[tuple[Resource, int], Response]:
        parser = default.parse_args()
        details = {
            'version': app.config['VERSION'],
            'apiVersions': app.config['API_VERSIONS'],
            'siteName': g.settings['site_name'],
            'imageProcessing': {
                'enabled': g.settings['image_processing'],
                'availableImageSizes':
                    app.config['IMAGE_SIZE']
                    if g.settings['image_processing'] else None},
            'IIIF': {
                'enabled': g.settings['iiif'],
                'url': g.settings['iiif_url'],
                'version': int(g.settings['iiif_version'])}}
        if parser['download']:
            download(details, backend_details_template(), 'content')
        return marshal(details, backend_details_template()), 200


class ClassMapping(Resource):
    @staticmethod
    def get() -> Union[tuple[Resource, int], Response]:
        return marshal([{
            "systemClass": class_.name,
            "crmClass": class_.cidoc_class.code,
            "view": class_.view,
            "icon": class_.icon,
            "en": class_.label}
            for class_ in g.classes.values() if class_.cidoc_class],
            class_overview_template()), 200


class SystemClassCount(Resource):
    @staticmethod
    def get() -> Union[tuple[Resource, int], Response]:
        return marshal(get_overview_counts(), overview_template()), 200
