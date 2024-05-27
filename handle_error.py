import time

error_log_file = 'error_log.txt'

# Log errors to a file
def log_error(error_message):
    with open(error_log_file, 'a') as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")
    print(f"Error: {error_message} ")
