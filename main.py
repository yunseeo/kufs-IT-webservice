from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

import crud

app = FastAPI(title="야풀이")

# 14_프론트엔드_활용 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#팀별 응원 포인트 총합
@app.get("/puri/team_rank")
def all_team_point():
    return crud.team_list()

#특정 팀 포인트
@app.get("/puri/team_point/{team_num}")
def the_team_point(team_num: int):
    return crud.my_team_point(team_num=team_num)

#회원가입
@app.post("/puri/signup")
def signup_route(
    user_id: str = Body(...), 
    user_pw: str = Body(...), 
    nickname: str = Body(...), 
    name: str = Body(...), 
    phone_num: str = Body(...), 
    email: str = Body(...), 
    team_num: int = Body(...)
):
    return crud.sign_up_user(user_id=user_id, user_pw=user_pw, nickname=nickname, name=name, phone_num=phone_num, email=email, team_num=team_num)

#퀴즈 랜덤 호출
@app.get("/puri/quiz")
def read_quiz_route():
    return crud.read_quiz()

#사용자 답 입력
@app.patch("/puri/quiz/{qzid}/{user_ans}")
def update_user_answer_route(qzid: int, user_ans: int):
    return crud.put_your_answer(qzid, user_ans)

#전체 퀴즈 조회
@app.get("/puri/quizlist")
def read_quiz_list_route():
    return crud.read_quiz_list()

#퀴즈 하나
@app.get("/puri/quiz/{qzid}")
def select_one_quiz(qzid: int):
    return crud.read_one_quiz(qzid)

#새 글 쓰기
@app.post("/puri/post")
def write_new_post(Title: str = Body(...), Content: str = Body(...)):
    return crud.write_new_post(Title=Title, Content=Content)

#글 수정
@app.patch("/puri/board/{PostNum}")
def update_post(PostNum: int, Title: str = Body(...), Content: str = Body(...)):
    return crud.update_post(Title=Title, Content=Content, PostNum=PostNum)

#글 삭제
@app.delete("/puri/board/{PostNum}")
def delete_post(PostNum: int):
    return crud.delete_post(PostNum=PostNum)

#전체 메인화면 불러오기
@app.get("/puri/board")
def read_all_posts():
    return crud.read_main_posts()

#전체 글 불러오기
@app.get("/puri/board_list")
def read_main_board():
    return crud.read_all_posts()

#로그인
@app.post("/puri/login")
def login_id(
    input_id: str = Body(...), 
    input_pw: str = Body(...)
):
    return crud.login(input_id, input_pw)

#로그아웃
@app.post("/puri/logout")
def logout():
    return crud.logout()

#내 정보
@app.get("/puri/mydata")
def mydata():
    return crud.mypage()

#온라인 접속 여부
@app.get("/puri/online")
def online_check():
    return crud.online()