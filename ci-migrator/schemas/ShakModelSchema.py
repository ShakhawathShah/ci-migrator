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

# schema = ShakModelSchema()
# result = schema.load(data)

# circleci_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
# print(circleci_yaml)
