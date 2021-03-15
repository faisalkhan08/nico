import os

filepath = os.getcwd()
def MakeFile(file_name):
    pwd = os.path.dirname(__file__)
    working_dir = "media/"
    directory = "media/"
    path = os.path.join(pwd, directory)
    os.makedirs(path)
    with open(working_dir + '/generate.py', 'w') as f:
        temp_path = working_dir + file_name
        file = open(file_name, 'w')
        file.write('import numpy as np\n')
        file.write('def print_success():\n')
        lis_is = [[12, 13, 12], [15, 16, 25]]
        for i in lis_is:
            file.write('\tprint (' + str(i) + ')\n')
        file.close()
        print('Execution completed.')


if __name__ == "__main__":
    MakeFile('generate.py')
