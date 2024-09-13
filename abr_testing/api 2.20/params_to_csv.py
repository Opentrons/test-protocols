


def find_params(contents):
    START_TAG = "def add_parameters"
    END_TAG = "### RUN ###"
    start_ind = contents.index(START_TAG)

    end_ind = contents.index(END_TAG)
    return contents[start_ind : end_ind]


def write_csv(params):
    



file_name = input("file: ")

file = open(file_name)

file_contents = file.read()


print(find_params(file_contents))