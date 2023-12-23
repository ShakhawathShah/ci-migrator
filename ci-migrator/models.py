import json
from re import S
from turtle import st
from typing import Dict, Optional
from dataclasses import asdict, dataclass


@dataclass
class CircleCIModel:
    version: float
    jobs: dict
    workflows: dict
    orbs: Optional[Dict] = None
    commands: Optional[Dict] = None
    parameters: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)

    def to_str(self):
        return json.dumps(asdict(self), indent=2)

    def to_shak_model(self):
        shak_name = "MY WORKFLOW"
        shak_trigger = {}
        for workflow_name, workflow_data in self.workflows.items():
            for job in workflow_data["jobs"]:
                shak_trigger["push"] = {
                    "branches": (
                        job["filters"].get("branches", None)
                        if job.get("filters")
                        else None
                    ),
                    "tags": (
                        job["filters"].get("tags", None) if job.get("filters") else None
                    ),
                }
        shak_parameters = self.parameters
        shak_jobs = {}
        for job_name, job_data in self.jobs.items():
            steps = []
            for step in job_data.get("steps"):
                name = step.get("run").get("name", None)
                run = step.get("run").get("command", None)
                converted_step = {"name": name, "run": run}
                steps.append(converted_step)
            shak_jobs[job_name] = {
                "env-var": job_data.get("environment"),
                "parameters": self.parameters,
                # "parameters": {param_name for param_name, param_data in job_data.get("parameters").items()},
                "image": job_data.get("docker")[0].get("image"),
                "steps": steps,
            }
        shak_run_order = []
        for workflow_name, workflow_data in self.workflows.items():
            for job in workflow_data["jobs"]:
                shak_run_order.append(
                    {
                        "name": list(job.keys())[0],
                        "depends-on": job.get("requires", None),
                    }
                )

        return ShakModel(
            name=shak_name,
            trigger=shak_trigger,
            parameters=shak_parameters,
            jobs=shak_jobs,
            run_order=shak_run_order,
        )

    def find_shak_trigger(self):
        for workflow in self.workflows.values():
            for job in list(workflow.values())[0]:
                if type(job) == str:
                    return {}
                if list(job.values())[0].get("filters") is not None:
                    return list(job.values())[0]
                else:
                    return {}


@dataclass
class ShakModel:
    name: str
    trigger: dict
    parameters: dict
    jobs: dict
    run_order: list

    def to_dict(self):
        # Convert the dataclass to a dictionary
        result_dict = asdict(self)
        # Update the key name
        result_dict["run-order"] = result_dict.pop("run_order")
        return result_dict

    def to_str(self):
        # Convert the dataclass to a dictionary
        result_dict = asdict(self)
        # Update the key name
        result_dict["run-order"] = result_dict.pop("run_order")
        return json.dumps(result_dict, indent=2)

    def to_circleci_model(self):
        # Extract the relevant data for CircleCIModel
        circleci_jobs = self.jobs
        circleci_workflows = {
            self.name: {
                "jobs": list(self.jobs.keys()),
            }
        }
        # if self.trigger:
        #     circleci_filters = {"filters": {list(self.trigger.keys())[0]: {"only": list(self.trigger.values())[0]}}}}

        return CircleCIModel(
            version=2.1, jobs=circleci_jobs, workflows=circleci_workflows
        )

    def to_github_model(self):
        # Extract relevant data for GitHubModel
        github_name = "MY WORKFLOW"
        github_on = self.trigger

        github_jobs = {}
        for job_name, job_data in self.jobs.items():
            steps = []
            for step in job_data.get("steps"):
                name = step.get("name", None)
                run = step.get("run", None)
                counter = 1
                step_data = {
                    "id": f"step {counter}",
                    "if": None,
                    "name": name,
                    "uses": None,
                    "run": run,
                    "with": job_data.get("parameters", None),
                    "working_directory": None,
                    "shell": None,
                    "env": job_data.get("env-var", None),
                }
                steps.append(step_data)
                counter += 1
            github_jobs[job_name] = {
                "name": job_name,
                "permissions": {},
                "needs": [
                    data.get("depends-on", None)
                    for data in self.run_order
                    if data.get("name") == job_name
                ],
                "if": None,
                "runs-on": [job_data.get("image")],
                "environment": None,
                "env": job_data.get("env-var"),
                "steps": steps,
                "continue-on-error": False,
                "container": {
                    "image": job_data.get("image"),
                    "env": job_data.get("env-var"),
                    "ports": [],
                    "volumes": [],
                    "options": "",
                },
            }

        return GitHubModel(
            name=github_name,
            on=github_on,
            jobs=github_jobs,
            run_name=github_name,
            env=self.parameters,
            permissions=None,
        )


@dataclass
class GitHubModel:
    name: str
    on: dict
    jobs: dict
    run_name: Optional[str] = None
    env: Optional[Dict] = None
    permissions: Optional[Dict] = None

    def to_dict(self):
        # Convert the dataclass to a dictionary
        result_dict = asdict(self)
        # Update the key name
        result_dict["run-name"] = result_dict.pop("run_name")
        return result_dict

    def to_str(self):
        # Convert the dataclass to a dictionary
        result_dict = asdict(self)
        # Update the key name
        result_dict["run-name"] = result_dict.pop("run_name")
        return json.dumps(result_dict, indent=2)

    # def to_shak_model(self):
    #     # Extract relevant data for ShakModel
    #     shak_name = "MY WORKFLOW"
    #     shak_jobs = self.jobs
    #     shak_trigger = self.on
    #     shak_image = list(self.jobs.values())[0].get("runs-on")

    #     return ShakModel(
    #         name=shak_name, trigger=shak_trigger, jobs=shak_jobs, image=shak_image
    #     )


@dataclass
class GitLabModel:
    name: str
    trigger: dict
    parameters: dict
    jobs: dict
    run_order: list

    def to_dict(self):
        return asdict(self)

    def to_str(self):
        return json.dumps(asdict(self), indent=2)
