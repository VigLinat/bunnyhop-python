from time import localtime, strftime

def log(log_str):
    time = strftime("%H:%M:%S", localtime())
    print(f"--LOG {time}: {log_str}")