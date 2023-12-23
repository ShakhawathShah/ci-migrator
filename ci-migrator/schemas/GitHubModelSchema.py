from dataclasses import field
from typing import Required
from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
)
import yaml


def validate_field(value):
    # Your custom validation logic here
    valid_values = ["read", "write", "none"]
    if value not in valid_values:
        raise ValidationError(f"Invalid value. Allowed values are {valid_values}.")


class StepSchema(Schema):
    id_token = fields.String(required=True, data_key="id")
    if_condition = fields.String(data_key="if", required=False, allow_none=True)
    name = fields.String(required=True)
    uses = fields.String(required=False, allow_none=True)
    run = fields.String(required=True)
    working_directory = fields.Str(required=False, allow_none=True)
    shell = fields.Str(required=False, allow_none=True)
    with_field = fields.Dict(
        data_key="with",
        keys=fields.Str(),
        values=fields.Str(),
        many=True,
        required=False,
        allow_none=True,
    )
    env = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=False, allow_none=True
    )


class PermissionsSchema(Schema):
    actions = fields.String(validate=validate_field)
    checks = fields.String(validate=validate_field)
    contents = fields.String(validate=validate_field)
    deployments = fields.String(validate=validate_field)
    id_token = fields.String(validate=validate_field, data_key="id")
    issues = fields.String(validate=validate_field)
    discussions = fields.String(validate=validate_field)
    packages = fields.String(validate=validate_field)
    pages = fields.String(validate=validate_field)
    pull_requests = fields.String(validate=validate_field)
    repository_projects = fields.String(validate=validate_field)
    security_events = fields.String(validate=validate_field)
    statuses = fields.String(validate=validate_field)


class EnvironmentSchema(Schema):
    name = fields.Str(required=True)
    url = fields.Str(required=False)


class ContainerSchema(Schema):
    image = fields.String(required=True)
    env = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=False, allow_none=True
    )
    ports = fields.List(fields.Integer(), required=False, allow_none=True)
    volumes = fields.List(fields.String(), required=False, allow_none=True)
    options = fields.String(required=False, allow_none=True)


class JobSchema(Schema):
    name = fields.Str(required=True)
    permissions = fields.Nested(PermissionsSchema, required=False)
    needs = fields.List(
        fields.Str(required=False, allow_none=True), required=False, allow_none=True
    )
    if_condition = fields.Str(data_key="if", required=True, allow_none=True)
    runs_on = fields.List(fields.Str(), required=False, data_key="runs-on")
    environment = fields.Nested(EnvironmentSchema, required=False, allow_none=True)
    env = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=False, allow_none=True
    )
    steps = fields.List(fields.Nested(StepSchema), required=True)
    continue_on_error = fields.Bool(required=False, data_key="continue-on-error")
    container = fields.Nested(ContainerSchema, required=True)


class FiltersSchema(Schema):
    branches = fields.List(fields.String(), required=False, allow_none=True)
    branches_ignore = fields.List(
        fields.String(), required=False, allow_none=True, data_key="branches-ignore"
    )
    tags = fields.List(fields.String(required=False), required=False, allow_none=True)
    tags_ignore = fields.List(
        fields.String(), required=False, allow_none=True, data_key="tags-ignore"
    )
    paths = fields.List(fields.String(), required=False, allow_none=True)
    paths_ignore = fields.List(
        fields.String(), required=False, allow_none=True, data_key="paths-ignore"
    )


class OnSchema(Schema):
    label = fields.Dict(
        types=fields.List(
            fields.String(validate=validate.OneOf(["created", "edited", "deleted"]))
        ),
        required=False,
    )
    issues = fields.Dict(
        types=fields.List(
            fields.String(validate=validate.OneOf(["opened", "labelled"]))
        ),
        required=False,
    )
    push = fields.Nested(FiltersSchema, required=False)
    pull_request = fields.Nested(FiltersSchema, required=False)


class GitHubModelSchema(Schema):
    name = fields.Str(required=True)
    run_name = fields.Str(data_key="run-name", required=False)
    on = fields.Nested(OnSchema, required=True)
    permissions = fields.Nested(PermissionsSchema, required=False, allow_none=True)
    env = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=False, allow_none=True
    )
    jobs = fields.Dict(keys=fields.Str(), values=fields.Nested(JobSchema))

# schema = GitHubModelSchema()
# result = schema.load(data)

# gh_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
# print(gh_yaml)
