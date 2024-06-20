import yaml
import os
import pprint
from .models import Backend, Task, Parameter, Job, Step


def read_cwl_file(cwl_path):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)
    base_name = os.path.splitext(os.path.basename(cwl_path))[0]
    cwl_class = cwl_data.get("class")

    # TODO: Transfer filename as Job/Task name
    if cwl_class == "Workflow":
        # print(f'[Detected] Workflow {cwl_file}')
        return parse_cwl_workflow(cwl_data, base_name)
    elif cwl_class == "CommandLineTool":
        # print(f'[Detected] CommandLineTool {cwl_file} ')
        return parse_cwl_clt(cwl_data, base_name)
    else:
        # TODO: Add error handling
        return "Unknown CWL class"


def parse_cwl_clt(cwl_data, name):
    def map_format(format_uri):
        EDAM_FORMAT_MAPPING = {
            "http://edamontology.org/format_1929": ".fasta",
            "http://edamontology.org/format_2330": ".fasta",
            "http://edamontology.org/format_1930": ".fastq",
            "http://edamontology.org/format_2572": ".bam",
            "http://edamontology.org/format_3016": ".vcf",
            "http://edamontology.org/format_3752": ".csv",
            "http://edamontology.org/format_3464": ".json",
        }

        # Check if format_uri is empty or not in the mapping
        if not format_uri or format_uri not in EDAM_FORMAT_MAPPING:
            return ".input"  # Default format if not found or empty
        else:
            return EDAM_FORMAT_MAPPING[format_uri]

    def parse_cwl_inputs(inputs: dict):
        parsed_inputs = []
        for input_name, input_data in inputs.items():
            input_type = input_data.get("type")
            input_binding = input_data.get("inputBinding", {})
            default_value = input_data.get("default")
            parsed_input = {
                "name": input_name,
                "type": input_type,
                "default": default_value,
                "input_binding": input_binding
            }
            parsed_inputs.append(parsed_input)
        return parsed_inputs

    def parse_cwl_outputs(outputs: dict):
        parsed_outputs = []
        for output_name, output_data in outputs.items():
            output_type = output_data.get("type")
            output_binding = output_data.get("outputBinding", {})

            # Example: Mapping CWL output to AA output format
            parsed_output = {
                "name": output_name,
                "type": output_type,
                "output_binding": output_binding
            }

            parsed_outputs.append(parsed_output)

        return parsed_outputs

    base_command = cwl_data.get("baseCommand")
    inputs = cwl_data.get("inputs", [])
    outpus = cwl_data.get("outputs", [])

    task = {
        # TODO: Add method to handle backend_id,
        #  incomplete_outputs_behaviour, custom_exit_status, custom_exit_behaviour
        "backend_id": 1,  # LOCALHOST
        "name": name,
        "base_command": base_command,
        "inputs": parse_cwl_inputs(inputs),
        "outputs": parse_cwl_outputs(outpus)
    }
    if 'stdout' in cwl_data:
        task['stdout_glob'] = f".{cwl_data.get('stdout').split('.')[-1]}"
    else:
        task['stdout_glob'] = ""

    executable_parts = [task['base_command']]
    in_globs = []
    for idx, input_data in enumerate(task['inputs']):
        input_position = 1
        position = input_data['input_binding']['position']
        type = input_data['type']
        # TODO: Need Error Handling of possible messy positions
        if type != 'File':
            executable_parts.append(f"$P{position}")
        else:
            executable_parts.append(f"$I{input_position}")
            input_position += 1
            if 'format' in input_data:
                in_globs.append(map_format(input_data['format']))
            else:
                in_globs.append('.input')

    executable = " ".join(executable_parts)
    in_glob = ",".join(in_globs)

    out_globs = []
    for idx, output_data in enumerate(task['outputs']):
        if output_data['type'] == 'File' and 'glob' in output_data['output_binding']:
            suffix = f".{output_data['output_binding'].get('glob').split('.')[-1]}"
            out_globs.append(suffix)
    out_glob = ",".join(out_globs)

    task['executable'] = executable
    task['in_glob'] = in_glob
    task['out_glob'] = out_glob

    # pp = pprint.PrettyPrinter(width=60)
    # pp.pprint(task)

    t = save_ctl_task(task)
    return t.id


def save_ctl_task(task_data: dict):
    def save_task_parameter(input_data: dict, task: object):
        if input_data['type'] == 'boolean':
            input_data['bool_valued'] = True
        else:
            input_data['bool_valued'] = False
        # TODO: Add method to manage rest_alias, spacing, switchless
        input_data["spacing"] = True
        input_data["switchless"] = False
        rest_alias = f"{task.name}_{input_data['name']}"
        flag = input_data['input_binding'].get('prefix')
        p = Parameter.objects.create(task=task)
        p.flag = flag
        p.default = input_data['default']
        p.bool_valued = input_data['bool_valued']
        p.rest_alias = rest_alias
        p.spacing = input_data["spacing"]
        p.switchless = input_data["switchless"]
        p.save()

    backend = Backend.objects.get(id=1)
    t = Task.objects.create(backend=backend)
    t.name = task_data['name']
    t.in_glob = task_data['in_glob']
    t.out_glob = task_data['out_glob']
    t.executable = task_data['executable']
    t.stdout_glob = task_data['stdout_glob']
    t.save()
    for idx, input_data in enumerate(task_data['inputs']):
        if input_data['type'] != 'File':
            # print(input_data, input_data['input_binding'].get('prefix'))
            save_task_parameter(input_data, t)
    return t

def parse_cwl_workflow(cwl_data, filename):
    steps = cwl_data.get("steps")

    for step_name, step_detail in steps.items():
        task_run = step_detail.get("run")
        task_class = task_run.get("class")

        if(task_class == "CommandLineTool"):
            task_id = parse_cwl_clt(task_run, step_name)
    
    j = Job.objects.create(name=filename, runnable=True)
    j.save()

    t = Task.objects.get(id=task_id)

    s = Step.objects.create(job=j, task=t, ordering=0)
    s.save()



