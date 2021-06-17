api_linked_place_template = {
    "@context": "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld",
    "type": "FeatureCollection",
    "features": [
        {
            "@id": "http://local.host/entity/104",
            "type": "Feature",
            "crmClass": "crm:E18 Physical Thing",
            "systemClass": "place",
            "properties": {
                "title": "Nostromos"
            },
            "description": [
                {
                    "value": "That is the Nostromos"
                }
            ],
            "when": {
                "timespans": [
                    {
                        "start": {
                            "earliest": "2018-01-31",
                            "latest": "2018-03-01"
                        },
                        "end": {
                            "earliest": "2019-01-31",
                            "latest": "2019-03-01"
                        }
                    }
                ]
            },
            "types": [
                {
                    "identifier": "http://local.host/api/0.2/entity/65",
                    "label": "Place",
                    "description": None,
                    "hierarchy": "",
                    "value": None,
                    "unit": None
                },
                {
                    "identifier": "http://local.host/api/0.2/entity/102",
                    "label": "Height",
                    "description": None,
                    "hierarchy": "Dimensions",
                    "value": 23,
                    "unit": "centimeter"
                }
            ],
            "relations": [
                {
                    "label": "Cargo hauler",
                    "relationTo": "http://local.host/api/0.2/entity/106",
                    "relationType": "crm:P1 is identified by",
                    "relationSystemClass": "appellation",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "Feature",
                    "relationTo": "http://local.host/api/0.2/entity/108",
                    "relationType": "crm:P46 is composed of",
                    "relationSystemClass": "feature",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "Height",
                    "relationTo": "http://local.host/api/0.2/entity/102",
                    "relationType": "crm:P2 has type",
                    "relationSystemClass": "type",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "Location of Nostromos",
                    "relationTo": "http://local.host/api/0.2/entity/105",
                    "relationType": "crm:P53 has former or current location",
                    "relationSystemClass": "object_location",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "Place",
                    "relationTo": "http://local.host/api/0.2/entity/65",
                    "relationType": "crm:P2 has type",
                    "relationSystemClass": "type",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "Datei",
                    "relationTo": "http://local.host/api/0.2/entity/112",
                    "relationType": "crm:P67i is referred to by",
                    "relationSystemClass": "file",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "GeoNames",
                    "relationTo": "http://local.host/api/0.2/entity/1",
                    "relationType": "crm:P67i is referred to by",
                    "relationSystemClass": "reference_system",
                    "type": "close match",
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                },
                {
                    "label": "https://openatlas.eu",
                    "relationTo": "http://local.host/api/0.2/entity/107",
                    "relationType": "crm:P67i is referred to by",
                    "relationSystemClass": "external_reference",
                    "type": None,
                    "when": {
                        "timespans": [
                            {
                                "start": {
                                    "earliest": None,
                                    "latest": None
                                },
                                "end": {
                                    "earliest": None,
                                    "latest": None
                                }
                            }
                        ]
                    }
                }
            ],
            "names": [
                {
                    "alias": "Cargo hauler"
                }
            ],
            "links": [
                {
                    "type": "close match",
                    "identifier": "https://www.geonames.org/2761369",
                    "referenceSystem": "GeoNames"
                }
            ],
            "geometry": {
                "type": "Point",
                "coordinates": [
                    9,
                    17
                ],
                "title": "",
                "description": ""
            },
            "depictions": [
                {
                    "@id": "http://local.host/api/0.2/entity/112",
                    "title": "Datei",
                    "license": "Open license",
                    "url": "N/A"
                }
            ]
        }
    ]
}

api_geojson_template = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                9,
                17
            ],
            "title": "",
            "description": ""
        },
        "properties": [
            {
                "@id": 104,
                "systemClass": "place",
                "name": "Nostromos",
                "description": "That is the Nostromos",
                "begin_earliest": "2018-01-31",
                "begin_latest": "2018-03-01",
                "begin_comment": "Begin of the Nostromos",
                "end_earliest": "2019-01-31",
                "end_latest": "2019-03-01",
                "end_comment": "Destruction of the Nostromos",
                "types": [
                    "Place",
                    "Height"
                ]
            }
        ]
    },
    {
        "type": "Feature",
        "geometry": None,
        "properties": [
            {
                "@id": 104,
                "systemClass": "place",
                "name": "Nostromos",
                "description": "That is the Nostromos",
                "begin_earliest": "2018-01-31",
                "begin_latest": "2018-03-01",
                "begin_comment": "Begin of the Nostromos",
                "end_earliest": "2019-01-31",
                "end_latest": "2019-03-01",
                "end_comment": "Destruction of the Nostromos",
                "types": [
                    "Place",
                    "Height"
                ]
            }
        ]
    }
]

api_geometries_template = [{'type': 'Feature',
                            'geometry':
                                {'coordinates': [9, 17], 'type': 'Point'},
                            'properties': [
                                {'id': 1,
                                 'name': '',
                                 'description': '',
                                 'objectId': 104,
                                 'objectDescription': 'That is the Nostromos',
                                 'objectName': 'Nostromos',
                                 'objectType': None,
                                 'shapeType': 'centerpoint'}]}]
