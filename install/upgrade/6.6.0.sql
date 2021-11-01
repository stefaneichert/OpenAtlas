-- Upgrade 6.5.0 to 6.6.0
-- Be sure to backup the database and read the upgrade notes before executing!

BEGIN;

-- #1563: OpenAtlas model to database

-- Renaming
ALTER TABLE model.class RENAME TO cidoc_class;
ALTER TABLE model.class_i18n RENAME TO cidoc_class_i18n;
ALTER TABLE model.class_inheritance RENAME TO  cidoc_class_inheritance;
ALTER SEQUENCE model.class_id_seq RENAME TO cidoc_class_id_seq;
ALTER SEQUENCE model.class_i18n_id_seq RENAME to cidoc_class_i18n_id_seq;
ALTER SEQUENCE model.class_inheritance_id_seq RENAME TO cidoc_class_inheritance_id_seq;
ALTER TABLE model.entity RENAME COLUMN class_code TO cidoc_class_code;
ALTER TABLE model.entity RENAME COLUMN system_class to openatlas_class_name;

-- Adding missing constraint for wewb.group table
ALTER TABLE ONLY web."group" ADD CONSTRAINT group_name_key UNIQUE (name);

-- New table model.openatlas_class
CREATE TABLE model.openatlas_class (
    id integer NOT NULL,
    name text NOT NULL,
    cidoc_class_code text,
    standard_type_id integer,
    alias boolean DEFAULT false,
    reference_system boolean DEFAULT false,
    write_access_group_name text,
    layout_color text,
    layout_icon text,
    created timestamp without time zone DEFAULT now() NOT NULL,
    modified timestamp without time zone
);
ALTER TABLE model.openatlas_class OWNER TO openatlas;
COMMENT ON TABLE model.openatlas_class IS 'A more fine grained use of CIDOC classes';
COMMENT ON COLUMN model.openatlas_class.alias IS 'If aliases are supported for entities with this class';
COMMENT ON COLUMN model.openatlas_class.reference_system IS 'If links to external reference systems are supported for entities with this class';
COMMENT ON COLUMN model.openatlas_class.layout_color IS 'For e.g. network vizualistaion';
COMMENT ON COLUMN model.openatlas_class.layout_icon IS 'For Bootstrap icons';

CREATE SEQUENCE model.openatlas_class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE model.openatlas_class_id_seq OWNER TO openatlas;
ALTER SEQUENCE model.openatlas_class_id_seq OWNED BY model.openatlas_class.id;

ALTER TABLE ONLY model.openatlas_class ALTER COLUMN id SET DEFAULT nextval('model.openatlas_class_id_seq'::regclass);
ALTER TABLE ONLY model.openatlas_class ADD CONSTRAINT openatlas_class_name_key UNIQUE (name);
ALTER TABLE ONLY model.openatlas_class ADD CONSTRAINT openatlas_class_pkey PRIMARY KEY (id);
ALTER TABLE ONLY model.openatlas_class ADD CONSTRAINT openatlas_class_cidoc_class_code_fkey FOREIGN KEY (cidoc_class_code) REFERENCES model.cidoc_class(code) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY model.openatlas_class ADD CONSTRAINT openatlas_class_standard_type_id_fkey FOREIGN KEY (standard_type_id) REFERENCES model.entity(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY model.openatlas_class ADD CONSTRAINT openatlas_class_write_access_group_name_fkey FOREIGN KEY (write_access_group_name) REFERENCES web."group"(name) ON UPDATE CASCADE ON DELETE CASCADE;
CREATE TRIGGER update_modified BEFORE UPDATE ON model.openatlas_class FOR EACH ROW EXECUTE PROCEDURE model.update_modified();

INSERT INTO model.openatlas_class (name, cidoc_class_code, alias, reference_system, write_access_group_name, layout_color, standard_type_id) VALUES
    ('acquisition',          'E8',  false, true,  'contributor', '#0000FF', (SELECT id FROM model.entity WHERE name = 'Event' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('activity',             'E7',  false, true,  'contributor', '#0000FF', (SELECT id FROM model.entity WHERE name = 'Event' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('actor_appellation',    'E82', false, false, 'contributor', NULL,      NULL),
    ('actor_actor_relation', NULL,  false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Actor actor relation' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('actor_function',       NULL,  false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Actor function' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('administrative_unit',  'E53', false, false, 'contributor', NULL,      NULL),
    ('appellation',          'E41', false, false, 'contributor', NULL,      NULL),
    ('artifact',             'E22', false, true,  'contributor', '#EE82EE', (SELECT id FROM model.entity WHERE name = 'Artifact' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('bibliography',         'E31', false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Artifact' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('edition',              'E31', false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Edition' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('external_reference',   'E31', false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'External reference' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('feature',              'E18', false, true,  'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Feature' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('file',                 'E31', false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'License' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('find',                 'E22', false, true,  'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Artifact' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('group',                'E74', true,  true,  'contributor', '#34623C', NULL),
    ('human_remains',        'E20', false, true,  'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Human remains' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('involvement',          NULL,  false, false, 'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Involvement' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('move',                 'E9',  false, true,  'contributor', '#0000FF', (SELECT id FROM model.entity WHERE name = 'Event' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('object_location',      'E53', false, false, 'contributor', '#00FF00', NULL),
    ('person',               'E21', true,  true,  'contributor', '#34B522', NULL),
    ('place',                'E18', true,  true,  'contributor', '#FF0000', (SELECT id FROM model.entity WHERE name = 'Place' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('reference_system',     'E32', false, false, 'manager',     NULL,      NULL),
    ('source',               'E33', false, true,  'contributor', '#FFA500', (SELECT id FROM model.entity WHERE name = 'Source' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('source_translation',   'E33', false, false, 'contributor', NULL,      NULL),
    ('stratigraphic_unit',   'E18', false, true,  'contributor', NULL,      (SELECT id FROM model.entity WHERE name = 'Stratigraphic unit' AND cidoc_class_code = 'E55' ORDER BY id ASC LIMIT 1)),
    ('type',                 'E55', false, true,  'editor',      NULL,      NULL);

ALTER TABLE ONLY model.entity ADD CONSTRAINT entity_openatlas_class_name_fkey FOREIGN KEY (openatlas_class_name) REFERENCES model.openatlas_class(name) ON UPDATE CASCADE ON DELETE CASCADE;

-- Update trigger functions for deleting related entities at delete to avoid orphaned data
DROP FUNCTION IF EXISTS model.delete_entity_related() CASCADE;
CREATE FUNCTION model.delete_entity_related() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            -- Delete aliases (P1, P131)
            IF OLD.cidoc_class_code IN ('E18', 'E21', 'E40', 'E74') THEN
                DELETE FROM model.entity WHERE id IN (SELECT range_id FROM model.link WHERE domain_id = OLD.id AND property_code IN ('P1', 'P131'));
            END IF;

            -- Delete location (E53) if it was a place, find or human remains
            IF OLD.cidoc_class_code IN ('E18', 'E20', 'E22') THEN
                DELETE FROM model.entity WHERE id = (SELECT range_id FROM model.link WHERE domain_id = OLD.id AND property_code = 'P53');
            END IF;

            -- Delete translations (E33) if it was a document
            IF OLD.cidoc_class_code = 'E33' THEN
                DELETE FROM model.entity WHERE id IN (SELECT range_id FROM model.link WHERE domain_id = OLD.id AND property_code = 'P73');
            END IF;

            RETURN OLD;
        END;

    $$;
ALTER FUNCTION model.delete_entity_related() OWNER TO openatlas;
CREATE TRIGGER on_delete_entity BEFORE DELETE ON model.entity FOR EACH ROW EXECUTE PROCEDURE model.delete_entity_related();

-- Merge web.hierarchy fields
ALTER TABLE web.hierarchy ADD COLUMN category text DEFAULT 'standard' NOT NULL;
UPDATE web.hierarchy SET category = 'custom' WHERE standard IS false;
UPDATE web.hierarchy SET category = 'value' WHERE value_type IS true;
UPDATE web.hierarchy SET category = 'system' WHERE locked IS true;
UPDATE web.hierarchy SET category = 'place' WHERE name IN ('Administrative unit', 'Historical place');
ALTER TABLE web.hierarchy DROP standard, DROP value_type, DROP locked;

-- Remodel web.hierarchy_form to web.hierarchy_openatlas_class
UPDATE web.form SET name = 'actor_function' WHERE name = 'member';
ALTER TABLE web.hierarchy_form RENAME TO hierarchy_openatlas_class;
ALTER TABLE web.hierarchy_openatlas_class ADD COLUMN hierarchy_name text;
UPDATE web.hierarchy_openatlas_class hc SET hierarchy_name =
    (SELECT name FROM web.hierarchy WHERE id = hc.hierarchy_id);
ALTER TABLE web.hierarchy_openatlas_class ADD COLUMN openatlas_class_name text;
UPDATE web.hierarchy_openatlas_class hc SET openatlas_class_name =
    (SELECT name FROM web.form WHERE id = hc.form_id);
ALTER TABLE web.hierarchy_openatlas_class DROP COLUMN form_id;
ALTER TABLE web.hierarchy_openatlas_class DROP COLUMN hierarchy_id;
ALTER TABLE ONLY web.hierarchy_openatlas_class
    ADD CONSTRAINT hierarchy_openatlas_class_hierarchy_name_openatlas_class_name_key
    UNIQUE (hierarchy_name, openatlas_class_name);
ALTER TABLE ONLY web.hierarchy_openatlas_class
    ADD CONSTRAINT hierarchy_openatlas_class_hierarchy_name_fkey
    FOREIGN KEY (hierarchy_name)
    REFERENCES web.hierarchy(name) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY web.hierarchy_openatlas_class
    ADD CONSTRAINT hierarchy_openatlas_class_openatlas_class_name_fkey
    FOREIGN KEY (openatlas_class_name)
    REFERENCES model.openatlas_class(name) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE web.hierarchy_openatlas_class ALTER COLUMN hierarchy_name SET NOT NULL;
ALTER TABLE web.hierarchy_openatlas_class ALTER COLUMN openatlas_class_name SET NOT NULL;

-- Remodel web.reference_system_form to web.reference_system_openatlas_class
ALTER TABLE web.reference_system_form RENAME TO reference_system_openatlas_class;
ALTER TABLE web.reference_system_openatlas_class ADD COLUMN openatlas_class_name text;
UPDATE web.reference_system_openatlas_class rc
   SET openatlas_class_name = (SELECT name FROM web.form WHERE id = rc.form_id);
ALTER TABLE web.reference_system_openatlas_class DROP COLUMN form_id;
ALTER TABLE ONLY web.reference_system_openatlas_class
    ADD CONSTRAINT reference_system_openatlas_class_openatlas_class_name_fkey
    FOREIGN KEY (openatlas_class_name)
    REFERENCES model.openatlas_class(name) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY web.reference_system_openatlas_class
    ADD CONSTRAINT reference_system_openatlas_class_reference_system_id_openatlas_class_name_key
    UNIQUE (reference_system_id, openatlas_class_name);

ALTER TABLE web.reference_system_openatlas_class ALTER COLUMN openatlas_class_name SET NOT NULL;

-- Drop obsolete web.form table
DROP TABLE web.form;

END;
