import csv
import pandas as pd
from io import StringIO  # StringIO를 추가
import datetime
from flask import Flask, render_template, request
import requests

# 10가지 체크 항목에 따라 점수화를 진행, 조건에 맞으면 1점, 아니면 0점으로 최소 0점 ~ 최대 10점으로 구성
app = Flask(__name__)

# 오늘 날짜
search_day = datetime.datetime.now().strftime("%y%m%d")

# CSV 파일 경로
csv_file = 'corp_code/filtered_data.csv'

@app.route('/')
def index():
    return render_template('index.html')

# 기본 검색
@app.route('/search', methods=['POST'])
def search():
    search_value = request.form['company_name']

    # CSV 파일 열기
    with open(csv_file, 'r', newline='') as file:
        csv_reader = csv.reader(file)

        # 헤더(첫 번째 행) 읽기
        header = next(csv_reader)

        # 검색할 열 인덱스 찾기 (예: 두 번째 열)
        search_column_index = header.index('기업명')

        # CSV 파일에서 검색
        for row in csv_reader:
            if row[search_column_index] == search_value:
                company_name = row[2]


    #재무제표 페이지
    url_a = 'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A'+str(company_name)+'&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701'

    #재무비율 페이지
    url_b = 'https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A'+str(company_name)+'&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701'

    # page 별 table 할당
    page_a = requests.get(url_a)
    page_b = requests.get(url_b)

    # HTML 문자열을 StringIO 객체로 래핑
    html_stringio_a = StringIO(page_a.text)
    html_stringio_b = StringIO(page_b.text)

    # StringIO 객체를 pd.read_html에 전달
    tables_a = pd.read_html(html_stringio_a)
    tables_b = pd.read_html(html_stringio_b)

    #기본 점수
    score = 0

    #### 점수화 조건 10가지
    #1. 영업 현금 흐름 > 0
    if pos_invCF(tables_a):
        score += 1

    #2. 영업 현금 흐름 > 순이익
    if ovr_invCF(tables_a):
        score += 1

    #3. 매출 증가율 > 자산 증가율
    if ovr_selIC(tables_a):
        score += 1

    # #4. ROA > 0
    if pos_roa(tables_b):
        score += 1

    # #5. ROA 전년 대비 증가
    if ovr_roaLY(tables_b):
        score += 1

    #6. 자기 자본 비율 > 50%
    if ovr_slfMP(tables_b):
        score += 1

    # #7. 유동비율 전년 대비 증가
    if ovr_mfLY(tables_b):
        score += 1

    # #8. 매출 총 이익율 전년 대비 증가
    if ovr_alsLY(tables_b):
        score += 1

    # #9. 부채 비율 < 100%
    if dec_dept(tables_b):
        score += 1

    # #10. ROE 3년 연속 > 15%
    if ovr_roeTY(tables_b):
        score += 1

    #점수 최소 0, 최대 10 제한
    score = min(10, score)
    print(score)



    # 오류 처리
    error_message = '검색 결과가 없거나 오류가 발생했습니다.'
    return render_template('index.html', error=error_message)

def pos_invCF(tab_a): # 영업이익 > 0
    value_a = tab_a[0]
    value_a = value_a.loc[[4]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = value_a[value_a.columns[4:5]].iloc[0,0]
    return value_a > 0

def ovr_invCF(tab_a): # 영업 이익 > 당기순이익
    value_a = tab_a[0]
    value_a = value_a.loc[[4]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = value_a[value_a.columns[4:5]].iloc[0,0] #영업이익

    value_b = tab_a[0]
    value_b = value_b.loc[[15]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b = value_b[value_b.columns[4:5]].iloc[0,0] #당기순이익
    return (value_a - value_b) > 0

def ovr_selIC(tab_a): #매출 증가율 > 자산 증가율
    value_a = tab_a[0]
    value_a = value_a.loc[[0]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = value_a[value_a.columns[-1:]].iloc[0,0] #매출액 증가율

    value_b = tab_a[2]
    value_b = value_b.loc[[0]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b_1 = value_b[value_b.columns[-1:]].iloc[0,0] #올해 자산
    value_b_2 = value_b[value_b.columns[2:3]].iloc[0,0] #작년 자산
    value_b_rt = ( value_b_1 - value_b_2 ) / value_b_2 * 100 #자산 증가율
    return ( value_a - value_b_rt ) > 0

def pos_roa(tab_b): #ROA > 0
    value_a = tab_b[0]
    value_a = value_a.loc[[19]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[-1:]].iloc[0,0])
    return value_a > 0.0

def ovr_roaLY(tab_b): #ROA가 작년에 비해 증가
    value_a = tab_b[0]
    value_a = value_a.loc[[19]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[2:3]].iloc[0,0]) #재작년 ROA

    value_b = tab_b[0]
    value_b = value_b.loc[[19]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b = float(value_b[value_b.columns[3:4]].iloc[0,0]) #작년 ROA
    return value_b - value_a > 0.0

def ovr_slfMP(tab_b): #자기 자본 비율 50% 이상
    value_a = tab_b[0]
    value_a = value_a.loc[[7]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[-1:]].iloc[0,0])
    return value_a > 50.0

def ovr_mfLY(tab_b): #유동비율 전년 대비 증가
    value_a = tab_b[0]
    value_a = value_a.loc[[1]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[-1:]].iloc[0,0]) #올해 유동 비율

    value_b = tab_b[0]
    value_b = value_b.loc[[1]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b = float(value_b[value_b.columns[3:4]].iloc[0,0]) #작년 유동 비율
    return  value_a - value_b > 0.0

def ovr_alsLY(tab_b): #매출 총 이익율 전년 대비 증가
    value_a = tab_b[0]
    value_a = value_a.loc[[15]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[-1:]].iloc[0,0]) #올해 매출 총 이익율

    value_b = tab_b[0]
    value_b = value_b.loc[[15]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b = float(value_b[value_b.columns[3:4]].iloc[0,0]) #올해 매출 총 이익율
    return value_a - value_b > 0.0

def dec_dept(tab_b): #부채 비율 < 100%
    value_a = tab_b[0]
    value_a = value_a.loc[[3]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[-1:]].iloc[0,0]) #올해 부채 비율
    return value_a < 100.0

def ovr_roeTY(tab_b): #10. ROE 3년 연속 > 15%
    value_a = tab_b[0]
    value_a = value_a.loc[[20]]
    value_a = value_a.set_index(value_a.columns[0])
    value_a = float(value_a[value_a.columns[1:2]].iloc[0,0]) #2년전 ROE

    value_b = tab_b[0]
    value_b = value_b.loc[[20]]
    value_b = value_b.set_index(value_b.columns[0])
    value_b = float(value_b[value_b.columns[2:3]].iloc[0,0]) #재작년 ROE

    value_c = tab_b[0]
    value_c = value_c.loc[[20]]
    value_c = value_c.set_index(value_c.columns[0])
    value_c = float(value_c[value_c.columns[3:4]].iloc[0,0]) #작년 ROE
    return ( value_a + value_b + value_c ) / 3.0 > 15.0

if __name__ == '__main__':
    app.run(debug=True)
