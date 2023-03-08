# 한국에스리 실시간 피드 구축

ArcGIS Online은 공간정보를 손쉽게 공유하고 사용할 수 있게해준다. 에스리 본사가 있는 미국은 다양한 고품질 데이터가 준비되어 있지만, 한국에 대한 데이터는 정확성과 최신성이 떯어지는 데이터가 많았다.

한국에스리 실시간 피드 구축 프로젝트는 ArcGIS 사용자가 곧바로 활용할 수 있는 데이터를 준비하기 위함이다.

## 실시간 대기정보
### 사용방법
1) 해당 리포지토리를 클론한다.
2) 새로운 환경변수 파일(`.env`)를 생성한다
3) 환경변수 파일에 필요한 환경변수를 작성한다
    - ESRI_USER : 한국에스리 포털 계정
    - ESRI_PW : 한국에스리 포털 계정 암호
    - AQI_URL : http://apis.data.go.kr/B552584/ArpltnInforInqireSvc
    - DATAGOKR_KEY : 공공데이터 API Key 
4) 필수 라이브러리를 설치한다
    - `conda install -c esri arcgis`
    - `conda install python-dotenv`
5) 스케쥴파일(`cron`)을 생성하고 다음과 같이 작성한다. *`cron`은 리눅스 환경에서만 테스트되었다*
    - `* * * * * 30 python3 feed.py`

    