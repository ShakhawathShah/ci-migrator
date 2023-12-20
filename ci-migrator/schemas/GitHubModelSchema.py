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
    if_condition = fields.String(data_key="if", required=False)
    name = fields.String(required=True)
    uses = fields.String(required=True)
    run = fields.String(required=True)
    working_directory = fields.Str(required=False)
    shell = fields.Str(required=False)
    with_field = fields.Dict(
        data_key="with", keys=fields.Str(), values=fields.Str(), many=True
    )
    env = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)


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
    env = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)
    ports = fields.List(fields.Integer(), required=False)
    volumes = fields.List(fields.String(), required=False)
    options = fields.String(required=False)


class JobSchema(Schema):
    name = fields.Str(required=True)
    permissions = fields.Nested(PermissionsSchema, required=False)
    needs = fields.List(fields.Str(), required=False)
    if_condition = fields.Str(data_key="if", required=True)
    runs_on = fields.List(fields.Str(), required=False)
    environment = fields.Nested(EnvironmentSchema, required=False)
    env = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)
    steps = fields.List(fields.Nested(StepSchema), required=True)
    continue_on_error = fields.Bool(required=False)
    container = fields.Nested(ContainerSchema, required=True)


class FiltersSchema(Schema):
    branches = fields.List(fields.String(), required=False)
    branches_ignore = fields.List(fields.String(), required=False)
    tags = fields.List(fields.String(), required=False)
    tags_ignore = fields.List(fields.String(), required=False)
    paths = fields.List(fields.String(), required=False)
    paths_ignore = fields.List(fields.String(), required=False)


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
    run_name = fields.Str(required=True)
    on = fields.Nested(OnSchema, required=True)
    permissions = fields.Nested(PermissionsSchema, required=False)
    env = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)
    jobs = fields.Dict(keys=fields.Str(), values=fields.Nested(JobSchema))


# Example usage:
data = {
    "name": "MyGitHubModel",
    "run_name": "MyGitHubRun",
    "on": {
        "label": {"types": ["created", "edited", "deleted"]},
        "issues": {"types": ["opened", "labelled"]},
        "push": {
            "branches": ["main"],
            "branches_ignore": ["master"],
            "tags": ["v2"],
            "tags_ignore": ["v1"],
            "paths": ["src"],
            "paths_ignore": ["docs"],
        },
        "pull_request": {
            "branches": ["feature"],
            "branches_ignore": ["bugfix"],
            "tags": ["v3"],
            "tags_ignore": ["v2"],
            "paths": ["src"],
            "paths_ignore": ["docs"],
        },
    },
    "permissions": {
        "actions": "read",
        "checks": "write",
        "contents": "none",
        "deployments": "read",
        "id": "none",
        "issues": "read",
        "discussions": "none",
        "packages": "write",
        "pages": "none",
        "pull_requests": "read",
        "repository_projects": "none",
        "security_events": "read",
        "statuses": "none",
    },
    "env": {"GITHUB_TOKEN": "secret-token", "MY_ENV_VARIABLE": "some-value"},
    "jobs": {
        "build_job": {
            "name": "Build",
            "permissions": {
                "actions": "read",
                "checks": "none",
                "contents": "write",
                "deployments": "none",
                "id": "read",
                "issues": "read",
                "discussions": "none",
                "packages": "write",
                "pages": "none",
                "pull_requests": "read",
                "repository_projects": "none",
                "security_events": "none",
                "statuses": "read",
            },
            "needs": ["test_job"],
            "if": "${{ github.event_name == 'push' }}",
            "runs_on": ["ubuntu-latest"],
            "environment": {"name": "production", "url": "https://example.com"},
            "env": {"MY_JOB_VARIABLE": "job-value"},
            "steps": [
                {
                    "id": "step1",
                    "if": "${{ success() }}",
                    "name": "Checkout code",
                    "uses": "actions/checkout@v2",
                    "run": "echo 'Checking out code'",
                },
                {
                    "id": "step2",
                    "if": "${{ github.event_name == 'pull_request' }}",
                    "name": "Build and test",
                    "uses": "some/action@v1",
                    "run": "echo 'Building and testing'",
                    "with": {"param1": "value1", "param2": "value2"},
                    "working_directory": "./temp",
                },
            ],
            "continue_on_error": False,
            "container": {
                "image": "docker-image",
                "env": {"DOCKER_ENV_VARIABLE": "docker-value"},
                "ports": [8080],
                "volumes": ["/data:/app/data"],
                "options": "--rm",
            },
        },
        "test_job": {
            "name": "Test",
            "permissions": {
                "actions": "write",
                "checks": "read",
                "contents": "none",
                "deployments": "read",
                "id": "write",
                "issues": "none",
                "discussions": "write",
                "packages": "read",
                "pages": "none",
                "pull_requests": "none",
                "repository_projects": "write",
                "security_events": "none",
                "statuses": "none",
            },
            "needs": [],
            "if": "${{ always() }}",
            "runs_on": ["ubuntu-latest"],
            "environment": {"name": "production", "url": "https://example.com"},
            "env": {},
            "steps": [
                {
                    "id": "step3",
                    "if": "someting",
                    "name": "Run tests",
                    "uses": "test/action@v1",
                    "run": "echo 'Running tests'",
                }
            ],
            "continue_on_error": True,
            "container": {
                "image": "test-image",
                "env": {},
                "ports": [],
                "volumes": [],
                "options": "",
            },
        },
    },
}


# schema = GitHubModelSchema()
# result = schema.load(data)

# gh_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
# print(gh_yaml)
