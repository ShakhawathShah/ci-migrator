# import yaml
# from ci_migrator.schemas.CircleCIModelSchema import CircleCIModelSchema
# from ci_migrator import cli


# def test_circleci():
#     config_file = ".circleci/config.yml"
#     file = open(config_file, 'r')
#     config_data = file.read()
#     circleci_config = yaml.safe_load(config_data)
#     circle_schema = CircleCIModelSchema()
#     result = circle_schema.load(circleci_config)