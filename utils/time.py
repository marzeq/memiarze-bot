import time
import re


def process_time(tme: str):
    tme = re.findall("..?", tme.replace(" ", ""))
    endtime = time.time()
    if not tme:
        raise ValueError("Nie podałeś właściwego czasu!")
    for tmearg in tme:
        if [tmearg.endswith(char) for char in "smhdMy"]:
            if not tmearg[:-1].isdigit():
                if tmearg[:-1] == "":
                    raise ValueError("Nie podałeś właściwego czasu!")
                raise ValueError(f"{tmearg} is invalid!")
            if tmearg.endswith("s"):
                endtime += int(tmearg.replace("s", ""))
            elif tmearg.endswith("m"):
                endtime += int(tmearg.replace("m", "")) * 60
            elif tmearg.endswith("h"):
                endtime += int(tmearg.replace("h", "")) * 3600
            elif tmearg.endswith("d"):
                endtime += int(tmearg.replace("d", "")) * 86400
            elif tmearg.endswith("M"):
                endtime += int(tmearg.replace("M", "")) * 2629800
            elif tmearg.endswith("y"):
                endtime += int(tmearg.replace("y", "")) * 31556952

    return endtime
