import os
from datetime import datetime, timezone, time


# 초기화 시간 파일 경로
#RESET_TIME_FILE = "db_reset_time.txt"

# 초기화 시간을 파일에 저장
#def save_reset_time():
#    with open(RESET_TIME_FILE, "w") as f:
#        f.write(datetime.now(timezone.utc).isoformat())

# 파일에서 초기화 시간 읽기
#def get_reset_time():
#    if not os.path.exists(RESET_TIME_FILE):
#        # 파일이 없으면 초기값으로 아주 과거의 시간을 반환
#        return datetime.min.replace(tzinfo=timezone.utc)
#    with open(RESET_TIME_FILE, "r") as f:
#        return datetime.fromisoformat(f.read().strip())

def stringToDatetime(input_date):
    _date = input_date.split('-')
    _date = list(map(int, _date))
    return datetime(_date[0], _date[1], _date[2], _date[3], _date[4], _date[5])

def stringToTime(input_time):
    _time = input_time.split(':')
    _time = list(map(int, _time))
    print(_time)
    return time(hour=_time[0], minute=_time[1], second=_time[2])