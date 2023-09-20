import multiprocessing
from record import record_dummy
from metadata import metadata
from send import send

record = record_dummy

# List of processes
if __name__ == "__main__":
    process_list =[
        multiprocessing.Process(target=record),
        multiprocessing.Process(target=metadata),
        multiprocessing.Process(target=send)
    ]

    for process in process_list:
        process.start()
    # for process in process_list:
    #     process.join()
