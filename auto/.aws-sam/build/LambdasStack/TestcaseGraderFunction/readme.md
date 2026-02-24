## Grader Documentation

- AWS Lambda creates a base initialisation process (PID 1) and a process for the python3.9 execution (PID 8).
- Whenever the `lambda-function` is invoked, we will create a subprocess (example PID 21) to execute the command (‘/code’). This process will take up an average of about 30MB of RAM, the base memory usage when we use resource.getrusage(maxrss). Executing this process with `subprocess.Popen` allows for obtaining time and memory information. 
- This command will create a further subprocess (example PID 22) that runs the code, which is the process that we are interested in. 
- We use cpu_times().user and memory_info().rss to calculate the time and memory usage of the codes. Additionally, we check for exceedingly long wall times (>20s) in case of stalling or other problems. 
- At the end of our code, we terminate all processes that are not our 2 base lambda processes, ensuring RAM and CPU are freed up to be dedicated for future invocations.

Limits
- We use an rlimit NOFILE of 4 (which represents the input and output files opened by the 2 processes).
	+ When programs create network connections, it typically opens a file descriptor to represent the connection. Therefore, if the maximum number of file descriptors allowed for the process is exceeded, new network connections may not be able to be created.
	+ Furthermore, this prevents writing extra output to files or reading from unauthorized files, especially during communication problems.
- We use an rlimit FSIZE of 128MB
	+ AWS Lambda has a limited ephemeral storage (/tmp) of 512MB, hence we limit each of the main files (input, output, comparison) to 128MB which ensures we do not exceed this limit.
	+ This is to prevent a wabbit fork bomb which would be able to use up lambda’s ephemeral storage and choke future submissions to the same container instance.
