import os
import shutil
import re
import datetime

class Case:
    def __init__(self, _id=0, part_length=0, cut_off=0, contains_text=False, case_type="", connection=""):
        self._id = _id
        self.part_length = part_length
        self.cut_off = cut_off
        self.contains_text = contains_text
        self.case_type = case_type
        self.connection = connection

folder_regex = re.compile(r"(\d+) \((\d+)\) ?(\-\d+)? ?([A-Za-z0-9\-^ ]+)?")
case_regex = re.compile(r"(?P<PDO>\w+-\w+-\d+)__\((?P<connection_type>[A-Za-z0-9;\-]+),(?P<id>\d+)\)\[?(?P<angle>[A-Za-z0-9\.\-#= ]+)?\]?(?P<file_type>\.\w+)")

def date_as_path(date=None):
    if(date == None):
        date = datetime.datetime.now().date()
    _day = f'D{"0"+str(date.day) if date.day < 10 else str(date.day)}'
    _month = f'M{"0"+str(date.month) if date.month < 10 else str(date.month)}'
    _year = f'Y{str(date.year)}'
    return os.path.join(_year, _month, _day)

LOCAL_STL_PATH = r"C:\Users\TruUser\Desktop\작업\스캔파일"
LOCAL_ESP_PATH = r"C:\Users\TruUser\Desktop/작업\작업저장"
LOCAL_PRG_PATH = r"C:\Users\TruUser\Documents\DP Technology\ESPRIT\Data\NC_Files"

REMOTE_STL_PATH = f"\\\\192.168.1.100\\Trubox\\####ERP_RM####\\{date_as_path()}\\1. CAM\\1. STL\Isaac"
REMOTE_ESP_PATH = f"//192.168.1.100/Trubox/####ERP_RM####/{date_as_path()}/1. CAM/2. ESP/Isaac"
REMOTE_PRG_PATH = f"//192.168.1.100/Trubox/####ERP_RM####/{date_as_path()}/1. CAM/3. NC files/Isaac"

def check_prg_files(prg_path) -> list[Case]:
    output = []
    for file in os.listdir(prg_path):
        c = Case()
        if(".prg" in file):
            with open(os.path.join(prg_path, file), 'r') as file:
                contents = file.read()

            c._id = contents.split('\n')[0][1:5]
            c.connection = contents.split('\n')[0].split('(')[1].split(')')[0]

            for i, line in enumerate(contents.split("\n")):
                if(i == 0):
                    if("ASC" in line):
                        c.case_type = "ASC"
                    elif("AOT" in line):
                        c.case_type = "AOT"
                    elif("TLOC" in line or "TLCS" in line):
                        c.case_type = "TLOC"
                    elif("T-L" in line):
                        c.case_type = "T-L"
                    else:
                        c.case_type = "DS"
                if("TEXT" in line):
                    c.contains_text = True
                if("(PartLength)" in line):
                    c.part_length = float(contents.split("\n")[i+1].split(' ')[1])
                if("CUT OFF" in line):
                    c.cut_off = float(contents.split("\n")[i-1][4:])
            output.append(c)
    return output

def get_folder_stats(path):
    folders = [folder_regex.match(file) for file in os.listdir(path) 
               if folder_regex.match(file) is not None]

    folder_count = len(folders)
    file_count = sum([int(i.group(2)) for i in folders])
    canceled_count = sum([int(i.group(3) if i.group(3) is not None else 0)*-1 for i in folders])

    path_data = {
        "folder-count": folder_count,
        "file-count": file_count,
        "canceled-count:": canceled_count
    }

    return path_data

def clear_stl_folder():
    files = os.listdir(LOCAL_STL_PATH)
    for file in files:
        if(case_regex.match(file) and case_regex.match(file).group("file_type") == ".stl"):
            os.remove(os.path.join(LOCAL_STL_PATH, file))
            
def import_stl_files(index=0):
    folders = [folder_regex.match(file) for file in os.listdir(REMOTE_STL_PATH) if folder_regex.match(file) is not None]
    folders = sorted(folders, key=lambda folder: (int(folder.group(1))))

    # TO-DO: Add exception handling.
    for file in os.listdir(os.path.join(REMOTE_STL_PATH,folders[index].group(0))):
        shutil.copy2(
            os.path.join(REMOTE_STL_PATH, folders[index].group(0), file),
            LOCAL_STL_PATH
        )

def upload_prg_files():
    if(len(os.listdir(LOCAL_PRG_PATH)) > 0):
        new_path_name = os.path.join(
            REMOTE_PRG_PATH, 
            f'{get_folder_stats(REMOTE_PRG_PATH)["folder-count"] + 1} ({len(os.listdir(LOCAL_PRG_PATH))})')
        
        os.mkdir(new_path_name)

        for file in os.listdir(LOCAL_PRG_PATH):
            shutil.move(os.path.join(LOCAL_PRG_PATH, file), new_path_name)

def upload_esp_files():
    case_count = len([
        case_regex.match(file) for file in os.listdir(LOCAL_ESP_PATH) 
        if case_regex.match(file) is not None and case_regex.match(file).group("file_type") == ".esp"
        ])
    
    if(case_count > 0):
        new_path_name = os.path.join(
            REMOTE_ESP_PATH,
            f'{get_folder_stats(REMOTE_ESP_PATH)["folder-count"] + 1} ({case_count})')
        
        os.mkdir(new_path_name)

        for file in os.listdir(LOCAL_ESP_PATH):
            if(case_regex.match(file) and case_regex.match(file).group("file_type") == ".esp"):
                shutil.move(os.path.join(LOCAL_ESP_PATH, file), new_path_name)


if __name__ == '__main__':
    for case in check_prg_files(LOCAL_PRG_PATH):
        print(case._id)