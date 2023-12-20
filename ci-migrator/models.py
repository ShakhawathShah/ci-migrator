import json
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
            for job in workflow_data['jobs']:
                shak_trigger["push"] = {
                    "branches": (job['filters'].get('branches', None) if job.get('filters') else None),
                    "tags": (job['filters'].get('tags', None)if job.get('filters') else None),
                }
        shak_parameters = self.parameters
        shak_jobs = {}
        for job_name, job_data in self.jobs.items():
            steps = []
            for step in job_data.get("steps"):
                name = step.get("name", None)
                run = step.get("run", None)
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
            for job in workflow_data['jobs']:
                # shak_run_order.append({
                #     "name": job.get('name', None),
                #     "depends-on": job.get('requires', None),
                # })
                shak_run_order.append({"name": list(job.keys())[0], "depends-on": job.get('requires', None) })

        return ShakModel(
            name=shak_name, trigger=shak_trigger, parameters=shak_parameters, jobs=shak_jobs, run_order=shak_run_order
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
        return asdict(self)

    def to_str(self):
        return json.dumps(asdict(self), indent=2)

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


@dataclass
class GitHubModel:
    name: str
    on: dict
    jobs: dict

    def to_dict(self):
        return asdict(self)

    def to_str(self):
        return json.dumps(asdict(self), indent=2)

    def to_shak_model(self):
        # Extract relevant data for ShakModel
        shak_name = "MY WORKFLOW"
        shak_jobs = self.jobs
        shak_trigger = self.on
        shak_image = list(self.jobs.values())[0].get("runs-on")

        return ShakModel(
            name=shak_name, trigger=shak_trigger, jobs=shak_jobs, image=shak_image
        )

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
    
