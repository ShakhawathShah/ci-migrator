import typer
import subprocess
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
            'type': 'list',
            'name': 'target_ci',
            'message': 'Select a target CI system: ',
            'choices': [
                        {
                            'name': 'CircleCI',
                        },
                        {
                            'name': 'Github Actions',
                        },
                        {
                            'name': 'Gitlab CI',
                        },
                        {
                            'name': 'Bitbucket Pipelines',
                        },
            ],
        }
    ]

    username = prompt(list_question)['target_ci']

    rprint("[yellow]=============================================[yello]")
    rprint(f"[green bold] You chose: {username} [green bold]")

    rprint("[yellow]=============================================[yello]")
    rprint("[red bold] Enter CircleCI Config File: [/red bold]")
    config_file = input()
    config_file = ".circleci/config.yml"
    rprint(f"[green bold] You entered: {config_file} [green bold]")
    rprint("[yellow]=============================================[yello]")
    rprint("[red bold] Enter Output File: [/red bold]")
    output_file = input()
    rprint(f"[green bold] You entered: {output_file} [green bold]")
    rprint("[yellow]=============================================[yello]")



@app.command("convert-github")
def convert_github():
    rprint("[red bold] Converting GitHub [/red bold]")


if __name__ == "__main__":
    app()
