# FS-report-API
재무제표 자동 분석 api

# 10 가지 조건에 따라 0 ~ 10점으로 투자 추천 점수 도출

#1. 영업 현금 흐름 > 0
#2. 영업 현금 흐름 > 당기순이익
#3. 매출 증가율 > 자산 증가율
#4. ROA > 0
#5. ROA 가 전년 대비 증가
#6. 자기 자본 비율 > 50%
#7. 유동 비율이 전년 대비 증가
#8. 매출 총 이익율이 전년 대비 증가
#9. 부채 비율 < 100%
#10. ROE가 3년 연속 15% 이상

# DB 연결 오류로 로컬에 존재하는 csv를 사용함

1. 상장 기업 검색
2. 해당 기업에 맞는 상장 코드 조회
3. 상장 코드로 재무제표 조회
4. 분석 및 점수 도출

# 따라서, db 연결 후 다음 작업을 진행해야 함

1. 상장 기업 검색
2. 점수 갱신일이 오늘인지 확인 ( 오늘이라면 점수 제공 )
3. 해당 기업에 맞는 상장 코드 조회
4. 상장 코드로 재무제표 조회
5. 분석 및 점수 도출
6. 점수 등록 및 점수 갱신일 갱신
