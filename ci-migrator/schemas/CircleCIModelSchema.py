from typing import Required
from marshmallow import Schema, fields, validates, validate, ValidationError
import yaml


class ParametersNameSchema(Schema):
    type = fields.Str(required=True)
    default = fields.Str(required=True)

    # @validates("type")
    # def validate_type(self, value):
    #     valid_types = ["str", "bool", "int"]  # Add more valid types as needed
    #     if value not in valid_types:
    #         raise ValidationError(
    #             f"Invalid type. Supported types: {', '.join(valid_types)}"
    #         )


class RunSchema(Schema):
    name = fields.Str()
    command = fields.Str(required=True)


class StepSchema(Schema):
    run = fields.Nested(RunSchema, required=True)


class CommandsSchema(Schema):
    description = fields.Str(required=True)
    parameters = fields.Dict(
        keys=fields.Str(), values=fields.Nested(ParametersNameSchema), many=True
    )
    steps = fields.Nested(StepSchema, many=True)


class DockerSchema(Schema):
    image = fields.Str(required=True)


class JobSchema(Schema):
    environment = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)
    parameters = fields.Dict(
        keys=fields.Str(), values=fields.Nested(ParametersNameSchema), many=True
    )
    docker = fields.List(fields.Nested(DockerSchema), many=True)
    steps = fields.Nested(StepSchema, many=True)


class ListOrStrField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value]
        else:
            self.fail("invalid")


class FilterSchema(Schema):
    branches = fields.Dict(
        only=ListOrStrField(validate=validate.Length(min=1)),
        ignore=ListOrStrField(validate=validate.Length(min=1)),
    )
    tags = fields.Dict(
        only=ListOrStrField(validate=validate.Length(min=1)),
        ignore=ListOrStrField(validate=validate.Length(min=1)),
    )


class WorkflowJobSchema(Schema):
    name = fields.Str(required=True)
    requires = fields.Str()
    context = fields.List(fields.Str())
    filters = fields.Nested(FilterSchema)


class WorkflowSchema(Schema):
    jobs = fields.List(fields.Dict(keys=fields.Str(), values=fields.Nested(WorkflowJobSchema)))


class CircleCIModelSchema(Schema):
    version = fields.Float(required=True)
    orbs = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)
    commands = fields.Dict(
        keys=fields.Str(), values=fields.Nested(CommandsSchema), many=True
    )
    parameters = fields.Dict(
        keys=fields.Str(), values=fields.Nested(ParametersNameSchema), many=True
    )
    jobs = fields.Dict(keys=fields.Str(), values=fields.Nested(JobSchema))
    workflows = fields.Dict(keys=fields.Str(), values=fields.Nested(WorkflowSchema))

    @validates("version")
    def validate_version(self, value):
        if value != 2.1:
            raise ValidationError("Invalid version. Only '2.1' is supported.")


# Example usage:
data = {
    "version": 2.1,
    "orbs": {"node": "node-orb", "python": "python-orb"},
    "commands": {
        "pip_install": {
            "description": "This is a pip install",
            "parameters": {
                "pip": {"type": "str", "default": "pip"},
                "version": {"type": "int", "default": "3"},
            },
            "steps": [{"run": {"name": "Install", "command": "pip install PyYaml"}}],
        },
        "aws_auth": {
            "description": "This is a aws auth command",
            "parameters": {
                "aws_account": {"type": "str", "default": "account1"},
                "aws_key": {"type": "str", "default": "password"},
            },
            "steps": [
                {"run": {"name": "aws auth", "command": "aws sso login"}},
                {"run": {"name": "Bye", "command": "echo 'Bye World!'"}},
            ],
        },
    },
    "parameters": {
        "global1": {"type": "str", "default": "hello"},
        "global": {"type": "bool", "default": "false"},
    },
    "jobs": {
        "node_install": {
            "environment": {"FOO": "bar"},
            "parameters": {
                "param1": {"type": "str", "default": "hello"},
                "param2": {"type": "bool", "default": "false"},
                "param3": {"type": "bool", "default": "false"},
            },
            "docker": [{"image": "node-image"}],
            "steps": [
                {"run": {"name": "Hello", "command": "echo 'Hello World!'"}},
                {"run": {"name": "Bye", "command": "echo 'Bye World!'"}},
            ],
        },
        "python_install": {
            "environment": {"BAR": "FOO"},
            "parameters": {
                "param1": {"type": "str", "default": "hello"},
            },
            "docker": [{"image": "python-image"}],
            "steps": [
                {"run": {"name": "Hello", "command": "echo 'Hello World!'"}},
            ],
        },
    },
    "workflows": {
        "workflow_name": {
            "jobs": [
                {
                    "job_one":{
                        "name": "job_one",
                        "requires": "previous",
                        "context": ["env1", "env2"],
                        "filters": {
                            "branches": {"only": "main", "ignore": ["master"]},
                            "tags": {"only": "1.2.3", "ignore": "0.0.0"},
                        },
                    }
                }
            ]
        }
    },
}


# schema = CircleCIModelSchema()
# result = schema.load(data)

# circleci_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
# print(circleci_yaml)

