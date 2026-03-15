#!/usr/bin/python
# The idea here is to generate scripts that can be run later on in the pipeline
# Some things are still hard-coded for convenience, but should be changed later
#       i.e. library_path, script_path, dacapo_path, renaissance_path, renaissance_jar, when calling the renaissance jar, & the references to the saraswati jar
import argparse
import shutil
import os
import json


def parse_args():
    parser = argparse.ArgumentParser(
        description="Experiment Generator", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-exp_path", "--exp_path", type=str,
                        help="Path where you want to generate the experiments")
    parser.add_argument("-java_path", "--java_path", type=str,
                        help="Path to specified java version", default="java")
    parser.add_argument("-python_path", "--python_path", type=str,
                        help="Path to python executable", default="python")
    parser.add_argument("-server_config", "--server_config", type=str,
                        help="Path to server config file")
    parser.add_argument("-target", "--target", type=str,
                        help="Path to target model/ratios")
    parser.add_argument("-baseline", "--baseline", default=False, action="store_true",
                        help="Turns off profiler to get baseline energy data")
    parser.set_defaults(verbose=False)

    return parser.parse_args()


def create_dir(str_dir):
    try:
        os.makedirs(str_dir, exist_ok=True)
    except FileExistsError:
        print("Directory already exists...skipping creation")
    except:
        print("OS error! Could not create %s" % (str_dir))
        quit()


def main():
    args = parse_args()
    exp_path = args.exp_path
    java_path = args.java_path
    python_path = args.python_path
    server_config = args.server_config
    target_path = args.target
    get_baseline = args.baseline
    iters = 256
    library_extra_papi = f"LD_LIBRARY_PATH={os.getcwd()}/bin/.:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
    library_path = f"{os.getcwd()}/bin"
    saraswati_jar = f"{os.getcwd()}/bazel-bin/saraswati_deploy.jar"
    dacapo_path = f"{os.getcwd()}/lib/dacapo.jar:{saraswati_jar}"
    renaissance_path = f"{os.getcwd()}/lib/renaissance-gpl-0.14.1.jar:{saraswati_jar}"
    renaissance_jar = f"{os.getcwd()}/lib/renaissance-gpl-0.14.1.jar"
    script_path = f"{os.getcwd()}/scripts"
    server_path = f"{os.getcwd()}/server/"
    gc = ""

    os.makedirs(exp_path, exist_ok=True)
    shutil.copyfile(server_config, os.path.join(exp_path, "server-config.json"))
    with open(server_config) as fp:
        tests = json.load(fp)
    server = tests["server"]
    clients = tests["client"]
    command = []
    for i in range(len(clients)):
        test = clients[i]
        benchmark = test["benchmark"]
        suite = test["suite"]
        output_directory = f'{exp_path}/{benchmark}'
        os.makedirs(output_directory, exist_ok=True)
        os.makedirs(f"{output_directory}/scratch", exist_ok=True)
        command.extend([
            f'{library_extra_papi} {java_path} {gc}',
            '-XX:+ExtendedDTraceProbes',
            f'-Dsaraswati.library.path={library_path}',
            f'-Dsaraswati.output.directory={output_directory}'])
        if "profiler_rate" in test:
            command.append(f'-Dsaraswati.async.period={test["profiler_rate"]}')
        if "jrapl" in server:
            command.append("-Dsaraswati.use.jrapl=Y")
        if get_baseline:
            command.append("-Dsaraswati.skip.profiler=Y")
        if suite == "dacapo":
            callback = 'SaraswatiDacapoCallback'
            size = test["size"]
            command.extend([
                f'-cp {dacapo_path}',
                f'Harness {benchmark} -s {size} -c saraswati.{callback}',
                f'--no-validation --iterations {iters}',
                f'--scratch-directory={output_directory}/scratch/'])
        elif suite == "renaissance":
            plugin = 'SaraswatiRenaissancePlugin'
            command.extend(
                [f'-cp {renaissance_path}', f'-jar {renaissance_jar}'])
            command.append(
                f'-r {iters} --plugin {saraswati_jar}!saraswati.{plugin} --policy {saraswati_jar}!saraswati.{plugin} --scratch-base={output_directory}/scratch/ {benchmark}')
        elif suite == "custom":
            main_class = test["main_class"]
            bench_args = test["args"].format(iters=iters)
            command.append(f'-cp {saraswati_jar} {main_class} {bench_args}')
        else:
            print(f'unrecognized suite {suite}! continuing...')
            continue

        command[-1] += ' &'
        command = [' \\\n    '.join(command)]
        command.append(f'pid_{i}=$!')
        command.append('sleep 5')
        command.append('')
        command = [' \n    '.join(command)]
    for i in range(len(clients)):
        command.append(f'tail --pid="${{pid_{i}}}" -f /dev/null')
    
    with open(f'{exp_path}/start.sh', "w") as output_file:
        transfer = "-t" if "transfer" in server else ""
        super_iteration = "-s" if "super_iteration" in server else ""
        baseline_flag = "-b" if get_baseline else ""
        output_file.write(f"{python_path} {server_path}/saraswati.py --output_directory={exp_path} --target={target_path} {transfer} {super_iteration} {baseline_flag}&\n")
        output_file.write("pid_server=$!\n")
        output_file.write('sleep 10\n')
        output_file.write('\n'.join(command))
        output_file.write('\ntail --pid="${pid_server}" -f /dev/null\n')        
        
if __name__ == '__main__':
    main()
