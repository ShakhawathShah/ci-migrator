from typing import Required
from marshmallow import Schema, fields, validates, validate, ValidationError
import yaml


class ParametersNameSchema(Schema):
    type = fields.Str(required=True)
    default = fields.Str(required=False)


class StepSchema(Schema):
    name = fields.String(required=True)
    run = fields.String(required=True)


class JobSchema(Schema):
    env_var = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        required=False,
        data_key="env-var",
        allow_none=True,
    )
    parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ParametersNameSchema),
        required=False,
        many=True,
        allow_none=True,
    )
    image = fields.Str(required=True)
    steps = fields.List(fields.Nested(StepSchema), required=True)


class FiltersSchema(Schema):
    branches = fields.List(fields.String(), required=False, allow_none=True)
    branches_ignore = fields.List(
        fields.String(), required=False, data_key="branches-ignore", allow_none=True
    )
    tags = fields.List(fields.String(), required=False, allow_none=True)
    tags_ignore = fields.List(
        fields.String(), required=False, data_key="tags-ignore", allow_none=True
    )


class TriggerSchema(Schema):
    push = fields.Nested(FiltersSchema, required=False, allow_none=True)
    pull_request = fields.Nested(
        FiltersSchema, required=False, data_key="pull-request", allow_none=True
    )


class RunOrderSchema(Schema):
    name = fields.Str(required=True)
    depends_on = fields.List(
        fields.Str(), data_key="depends-on", required=False, allow_none=True
    )


class ShakModelSchema(Schema):
    name = fields.Str(required=True)
    trigger = fields.Nested(TriggerSchema, required=True)
    parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ParametersNameSchema),
        required=False,
        many=True,
        allow_none=True,
    )
    jobs = fields.Dict(
        keys=fields.Str(), values=fields.Nested(JobSchema), required=True
    )
    run_order = fields.List(
        fields.Nested(RunOrderSchema), data_key="run-order", required=True
    )


# Example usage:
data = {
    "name": "shak workflow",
    "trigger": {
        "push": {
            "branches": ["main"],
            "branches-ignore": ["master"],
            "tags": ["v2"],
            "tags-ignore": ["v1"],
        },
    },
    "parameters": {
        "global1": {"type": "str", "default": "hello"},
        "global": {"type": "bool", "default": "false"},
    },
    "jobs": {
        "node_install": {
            "env-var": {"FOO": "bar"},
            "parameters": {
                "param1": {"type": "str", "default": "hello"},
                "param2": {"type": "bool", "default": "false"},
            },
            "image": "image_name",
            "steps": [
                {
                    "name": "Checkout code",
                    "run": "echo 'Checking out code'",
                },
                {
                    "name": "Build and test",
                    "run": "echo 'Building and testing'",
                },
            ],
        }
    },
    "run-order": [
        {
            "name": "job_one",
        },
        {
            "name": "job_two",
            "depends-on": ["previous"],
        },
    ],
}


# schema = ShakModelSchema()
# result = schema.load(data)

# circleci_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
# print(circleci_yaml)
