import typer
from PyInquirer import prompt, print_json, Separator
from rich import print as rprint
import yaml
from models import CircleCIModel, GitHubModel, GitLabModel, ShakModel
from schemas.CircleCIModelSchema import CircleCIModelSchema
from schemas.GitHubModelSchema import GitHubModelSchema
from schemas.ShakModelSchema import ShakModelSchema

app = typer.Typer()


@app.command("convert-circleci")
def convert_circleci():
    rprint("[red bold] Converting CircleCI [/red bold]")

    list_question = questions = [
        {
            "type": "list",
            "name": "target_ci",
            "message": "Select a target CI system: ",
            "choices": [
                # {
                #     'name': 'CircleCI',
                # },
                {
                    "name": "Github Actions",
                },
                {
                    "name": "Gitlab CI",
                },
                {
                    "name": "Bitbucket Pipelines",
                },
            ],
        }
    ]

    target_ci = prompt(list_question)["target_ci"]

    rprint("[yellow]=============================================[yello]")
    rprint(f"[green bold] You chose: {target_ci} [green bold]")

    rprint("[yellow]=============================================[yello]")
    rprint("[red bold] Enter CircleCI Config File: [/red bold]")
    config_file = input()
    # config_file = ".circleci/config.yml"
    rprint(f"[green bold] You entered: {config_file} [green bold]")
    rprint("[yellow]=============================================[yello]")
    rprint("[red bold] Enter Output File: [/red bold]")
    output_file = input()
    rprint(f"[green bold] You entered: {output_file} [green bold]")
    rprint("[yellow]=============================================[yello]")

    shak_instance = convert_to_shak(config_file)

    if target_ci == "Github Actions":
        github_instance = convert_to_github(shak_instance)
        github_yaml = yaml.dump(
            github_instance.to_dict(), default_flow_style=False, sort_keys=False
        )
        # Write to a file
        with open(output_file, "w") as f:
            f.write(github_yaml)


@app.command("convert-github")
def convert_github():
    rprint("[red bold] Converting GitHub [/red bold]")


def convert_to_shak(config_file: str):
    """Converts a CircleCI config file to a Shak config file"""
    rprint("[red bold] Converting to Shak [/red bold]")

    with open(config_file, "r") as f:
        config_data = f.read()
        print(config_data)
        circleci_config = yaml.safe_load(config_data)
        circle_schema = CircleCIModelSchema()
        result = circle_schema.load(circleci_config)

        circleci_instance = CircleCIModel(**result)
        # Convert CircleCIModel to ShakModel
        shak_instance = circleci_instance.to_shak_model()
        rprint(
            "[yellow]=====================Converting-To-Shak========================[yello]"
        )
        # print(circleci_instance)
        print(circleci_instance.to_str())
        # Display the ShakModel instance
        rprint(
            "[yellow]=========================Shak-Output====================[yello]"
        )
        # print(shak_instance)
        shak_schema = ShakModelSchema()
        shak_result = shak_schema.load(shak_instance.to_dict())
        # print(shak_result)
        print(shak_instance.to_str())

    # Return the ShakModel instance if valid
    return shak_instance


def convert_to_github(shak_instance: str):
    """Converts a Shak config file to a GitHub config file"""
    rprint("[red bold] Converting to GitHub [/red bold]")

    # Convert ShakModel to GitHubModel
    github_instance = shak_instance.to_github_model()
    rprint(
        "[yellow]=====================Converting-To-GitHub========================[yello]"
    )
    # print(circleci_instance)
    print(shak_instance.to_str())
    # Display the GitHubModel instance
    rprint("[yellow]=========================GitHub-Output====================[yello]")
    # print(github_instance)
    github_schema = GitHubModelSchema()
    github_result = github_schema.load(github_instance.to_dict())
    # print(github_result)
    # Return the GitHubModel instance if valid
    return github_instance


if __name__ == "__main__":
    app()
