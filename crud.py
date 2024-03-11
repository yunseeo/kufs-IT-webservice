import platform #macos냐 windows냐 확인.  
from sqlalchemy import create_engine, text

db_info = {
    'user': 'qa5rluyvoxqi5sskpub3',
    'pwd': 'pscale_pw_1JDGktfSmt9I1lo0dJR97BC9yCqmSekqNXIzRMdqW1P',
    'host': 'aws.connect.psdb.cloud',
    'port': 3306,
    'db': 'kusf-sbg'
}

if platform.system() == 'Darwin':
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{db_info['user']}:{db_info['pwd']}@{db_info['host']}:{db_info['port']}/{db_info['db']}?charset=utf8mb4&ssl=true"
else:
    SQLALCHEMY_DATABASE_URL = f"mysql://{db_info['user']}:{db_info['pwd']}@{db_info['host']}:{db_info['port']}/{db_info['db']}?charset=utf8mb4&ssl=true"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
)

#팀별 응원 포인트 총합
def team_list():

    i = 0
    data = []

    for i in range(11):

        team_num = i

        with engine.connect() as conn:
            rows = conn.execute(text("SELECT m.team_num, t.team_name, SUM(m.my_point) AS team_point FROM my_page AS m LEFT OUTER JOIN team_connect AS t ON m.team_num = t.team_num WHERE t.team_num = :team_num GROUP BY t.team_num, t.team_name, m.team_num"),
            {'team_num': team_num})

        columns = rows.keys()

        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)

    sorted_data = sorted(data, key=lambda x: x['team_point'], reverse=True)

    return sorted_data

#특정 팀 포인트
def my_team_point(team_num: int):

    data1 = []
    data2 = []

    with engine.connect() as conn:
        rows1 = conn.execute(text("SELECT m.team_num, t.team_name, SUM(m.my_point) AS team_point FROM my_page AS m LEFT OUTER JOIN team_connect AS t ON m.team_num = t.team_num WHERE t.team_num = :team_num GROUP BY t.team_num, t.team_name, m.team_num"),
        {'team_num': team_num})
        rows2 = conn.execute(text("SELECT nickname, my_point FROM my_page WHERE team_num = :team_num ORDER BY my_point DESC"),
        {'team_num': team_num})


    columns1 = rows1.keys()
    columns2 = rows2.keys()

    for row in rows1:
        data_dict1 = {column: row[idx] for idx, column in enumerate(columns1)}
        data1.append(data_dict1)

    for row in rows2:
        data_dict2 = {column: row[idx] for idx, column in enumerate(columns2)}
        data2.append(data_dict2)

    data1[0]['team_points_history'] = data2

    return data1

#회원가입
def sign_up_user(user_id, user_pw, nickname, name, phone_num, email, team_num):
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO my_page (user_id, user_pw, nickname, name, phone_num, email, team_num, my_point, online) VALUES (:user_id, :user_pw, :nickname, :name, :phone_num, :email, :team_num, 0, 0)"),
                {'user_id': user_id, 'user_pw': user_pw, 'nickname': nickname, 'name': name, 'phone_num': phone_num, 'email': email, 'team_num': team_num})
            conn.commit()

        return {"message": "회원가입이 완료되었습니다."}

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return {"message": "회원가입 중 오류가 발생했습니다."}

#퀴즈 랜덤 호출
def read_quiz(): 
    '''퀴즈 랜덤하게 1개만  조회하는 함수'''
    with engine.connect() as conn:
        rows = conn.execute(
            text("select qzid, content, option1, option2, option3, option4 from quiz where check_ans != 1 group by qzid order by rand() limit 1 ")
        )
        columns = rows.keys()

        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)

        qzid = data[0]['qzid']

    return data

#온라인 사용자에게 점수 부여
def update_user_point(user_point):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE my_page SET my_point = my_point + :user_point WHERE online = 1"),
            {'user_point': user_point}
        )
        conn.commit()

#사용자 답 입력 프론트엔드에서 받아와 실행하는 함수
def put_your_answer(qzid, user_ans):

    with engine.connect() as conn:
        #첫 번째 쿼리.
        conn.execute(
            text("UPDATE quiz SET user_ans = :user_ans where qzid = :qzid"),
            {'user_ans': user_ans, 'qzid': qzid}
        )

        #두 번째 쿼리.
        conn.execute(
            text("UPDATE quiz SET check_ans = 1 where user_ans = answer and qzid = :qzid"),
            {'qzid': qzid}
        )

        #세 번째 쿼리.
        conn.execute(
            text("UPDATE quiz SET check_ans = 0 where user_ans != answer and qzid = :qzid"),
            {'qzid': qzid}
        )

        #네 번째 쿼리.
        conn.execute(
            text("UPDATE quiz SET user_point = FLOOR(RAND() * 20 + 1) * 5 where check_ans = 1 and qzid = :qzid"), #5점 간격으로 포인트 랜덤 생성. 이제 어떻게 하면 큰 포인트는 적은 확률로 나오게 할 수 있을지 고민.
            {'qzid': qzid} #?
        )
        conn.commit()

        #다섯 번째 쿼리.
        rows = conn.execute(
            text("select check_ans, user_point from quiz where qzid = :qzid"),
            {'qzid': qzid}
        )
        columns = rows.keys()

        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)

        check_ans = data[0]['check_ans']
        user_point = data[0]['user_point']

        rows2 = conn.execute(
            text("SELECT * FROM my_page WHERE online = 1")
        )
        data2 = rows2.fetchall()  # 모든 행을 가져옴
        
        if len(data2) >= 1:
            if check_ans ==1: 
                update_user_point(user_point)
                message = f"정답입니다! 포인트 {user_point}점을 얻으셨습니다."
            else:
                message = "틀렸습니다."
        else:
            message = 1

    return message

#퀴즈 전체 목록
def read_quiz_list(): 
    with engine.connect() as conn:
        rows = conn.execute(
            text("select qzid, content from quiz group by qzid order by qzid desc")
        )
        columns = rows.keys()

        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)

    return data

#퀴즈 하나
def read_one_quiz(qzid: int):
    with engine.connect() as conn:
        rows = conn.execute(
            text("select qzid, content, option1, option2, option3, option4 from quiz WHERE qzid = :qzid"),
            {'qzid': qzid}
        )
        columns = rows.keys()

        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)

    return data

#새 글 쓰기
def write_new_post(Title: str, Content: str):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO board (Title, Content) VALUES (:Title, :Content)"),
            {'Title': Title, 'Content': Content}
        )
        conn.commit()

    return {"message": "글 생성 성공"}

#글 수정
def update_post(Title: str, Content: str, PostNum: int):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE board SET Title = :Title, Content = :Content WHERE PostNum = :PostNum"),
            {'Title': Title, 'Content': Content, 'PostNum': PostNum}
        )
        conn.commit()

    return {"message": "글 수정 성공"}

#글 삭제
def delete_post(PostNum: int):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM board WHERE PostNum = :PostNum"),
            {'PostNum': PostNum}
        )
        conn.commit()
    
    return {"message": "글 삭제 성공"}

#메인 화면 게시글 불러오기
def read_main_posts():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM board ORDER BY PostNum DESC LIMIT 10")
        )

    columns = rows.keys()

    data = []
    for row in rows:
        data_dict = {column: row[idx] for idx, column in enumerate(columns)}
        data.append(data_dict)

    return data

#전체 글 불러오기
def read_all_posts():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM board ORDER BY PostNum DESC")
        )

    columns = rows.keys()

    data = []
    for row in rows:
        data_dict = {column: row[idx] for idx, column in enumerate(columns)}
        data.append(data_dict)

    return data

#로그인 방식
def login(input_id: str, input_pw: str):
    with engine.connect() as conn:
        
        # 사용자 로그인 확인
        rows = conn.execute(
            text("SELECT user_pw FROM my_page WHERE user_id = :input_id"),
            {'input_id': input_id}
        )
        
        columns = rows.keys()

        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)
        print(data)
        
        if input_id != '':
            if input_pw != '':
                if data[0]['user_pw'] == input_pw:
                    conn.execute(
                        text("UPDATE my_page SET online = 1 WHERE user_id = :input_id"),
                        {'input_id': input_id}
                    )
                    conn.commit()
                    return {"message": "로그인 성공"}
                else:
                    return {"message": "로그인 실패"}
            else:
                return {"message": "비밀번호를 입력하세요"}
        else:
            return {"message": "아이디를 입력하세요"}

#로그아웃
def logout():
    with engine.connect() as conn: 
        conn.execute(
        text("UPDATE my_page SET online = 0 WHERE online = 1")
        )
        conn.commit()
    return {"message": "로그아웃"}

#마이페이지
def mypage():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT m.user_id, m.nickname, m.name, m.phone_num, m.email, m.my_point, t.team_name FROM my_page AS m LEFT OUTER JOIN team_connect AS t ON m.team_num = t.team_num WHERE m.online = 1;1")
        )
        columns = rows.keys()
        data = []
        for row in rows:
            data_dict = {column: row[idx] for idx, column in enumerate(columns)}
            data.append(data_dict)
    return data

#온라인 여부 확인
def online():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM my_page WHERE online = 1")
        )
        data = rows.fetchall()  # 모든 행을 가져옴
        
        if len(data) >= 1:
            return 1
        else:
            return 0