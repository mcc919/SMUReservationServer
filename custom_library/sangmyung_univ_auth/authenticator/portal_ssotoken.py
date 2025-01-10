import requests


def authenticate(username: str, password: str):
    with requests.session() as session:
        url = 'https://smsso.smu.ac.kr/Login.do'
        user_info = {'user_id': username, 'user_password': password}
        request = session.post(url, data=user_info)
        session.get('https://smul.smu.ac.kr/index.do')
        if request.url != url:
            return session


def get_data(session, username: str, url: str) -> dict:
    response = session.post(url, data={'@d#': '@d1#', '@d1#tp': 'dm', '_AUTH_MENU_KEY': 'usrCPsnlInfoUpd-STD', '@d1#strStdNo': username})
    return response.json()


def get_userinfo(session, username: str) -> dict:
    response = get_data(session, username, 'https://smul.smu.ac.kr/UsrSchMng/selectStdInfo.do')
    data = response['dsStdInfoList'][0]
    return {
        'name': data['NM_KOR'],
        'department': data['TMP_DEPT_MJR_NM'].split()[-1],
        'email': data['EMAIL']
    }


def get_detail(session, username: str) -> dict:
    response = get_data(session, username, 'https://smul.smu.ac.kr/UsrSchMng/selectStdInfo.do')
    data = response['dsStdInfoList'][0]
    return {
        'name': data['NM_KOR'],
        'username': data['STDNO'],
        'department': data['TMP_DEPT_MJR_NM'].split()[-1],
        'email': data['EMAIL'],
        #'year': data['SHYR'],
        #'semester': data['CMP_SMT']

        # add more fields modifed by @ryanhan919@gmail.com
        'nationality': data['NAT_RCD_NM'],
        'name_eng': data['NM_ENG'],
        'name_chinese': data['NM_CHA'],
        'grade': data['SHYR'],
        'enrollment_status': data['SCH_STAT_RCD_NM'],   # only '재학' students are allowed to reserve a room.
    }


def get_courses(session, username: str) -> list:
    response = get_data(session, username, 'https://smul.smu.ac.kr/UsrRecMatt/list.do')
    return response['dsRecMattList']
