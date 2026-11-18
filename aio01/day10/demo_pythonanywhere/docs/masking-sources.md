# 초기 마스킹 규칙 조사

확인일: **2026-10-27 (Asia/Seoul)**. 실행 시 네트워크를 사용하지 않으며 확인한 자료에서 선별한 초기 규칙을 함께 배포합니다.

## 채택 자료와 이용 조건

- 저작자·프로젝트: **LDNOOBW / List of Dirty, Naughty, Obscene, and Otherwise Bad Words**
- [한국어 원본 목록](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/ko)
- [원문 데이터 확인](https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/ko)
- [저장소 라이선스](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/blob/master/LICENSE): [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- 로컬 배포 파일: `app/data/initial_rules.json`. 저작자·출처 URL·라이선스·확인 날짜와 변경 설명을 파일에도 기록했습니다.

변경 사항: 전체 목록을 그대로 복제하지 않고 명확한 모욕·비하 표현 12개를 선별했습니다. 분리 기호를 넣은 변형 탐지용 정규식 1개는 이 프로젝트에서 자체 작성했습니다. 제공된 초기 규칙에는 위 출처에 대한 표시와 CC BY 4.0 라이선스 링크를 유지해야 합니다.

## 선별 기준과 제외 범위

일반 단어로도 쓰이는 단어, 신체·성 관련 단어의 일괄 차단, 광범위한 부분 문자열 차단은 초기 목록에서 제외했습니다. 예를 들어 일반 명사·정상 문장까지 가리는 규칙은 데모에서 오탐이 크므로 보수적으로 선택했습니다. 지역·집단 비하는 일부 명시적 비하어만 포함하며 전체 혐오 표현을 포괄하지 않습니다.

다른 방식도 비교했습니다. [Xim-ya의 한국어 필터](https://github.com/Xim-ya/korean_profanity_filter)는 변형 표현을 정규식으로 다루고, [lisuugi의 필터](https://github.com/lisuugi/korean-profanity-filter)는 탐지 수준과 우회 표현을 구분합니다. 이 프로젝트는 해당 소스 코드·복잡한 정규식·대용량 사전을 복제하지 않았습니다. 자료의 최신 조회 상태를 확인했다는 의미이며, 모든 최신 은어나 유해 표현을 수집했다는 의미는 아닙니다.

## 동작과 한계

- 원문에서 규칙별 일치 구간을 찾고 겹친 구간을 합쳐 문자 수에 맞는 `*`로 표시합니다.
- 키워드는 메타문자를 해석하지 않습니다. 정규식은 Python regex 문법이며 i/m/s 옵션을 지원합니다. JavaScript 전용 문법은 사용하지 않습니다.
- 패턴 최대 200자, 규칙 최대 200개, 글 5,000자, 댓글 1,000자, 규칙별 매칭 최대 20ms, 요청 내 전체 마스킹 예산 200ms입니다. 환경 부하에 따라 대체 안내가 표시될 수 있습니다.
- 빈 구간에 일치하는 패턴은 등록 시 대표 입력으로 거부하고, 실제 콘텐츠에서 발견하면 원문 대신 안내로 처리합니다. 모든 패턴의 안전성을 정적으로 증명하는 방식은 아닙니다.
- 시간 초과·손상된 규칙은 원문을 그대로 보여주지 않고 대체 안내로 처리합니다.
- 관리자 변경은 기존 글·댓글의 다음 표시에도 적용됩니다. 삭제한 초기 규칙은 재시작·init-db 재실행 때 복원하지 않습니다.
- 부분 문자열 탐지이므로 문맥에 따른 오탐과 미탐이 있습니다. 숫자·자모·동형 문자 등 모든 우회 표기, 문맥에 의한 혐오·위협 판단은 지원하지 않습니다. 관리자 검토와 지속적인 규칙 조정이 필요합니다.
