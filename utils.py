import os
from datetime import datetime, timezone


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