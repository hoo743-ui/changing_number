# Changing Number — Repository Guide

이 저장소는 행정 업무에서 반복되던 파일 / 폴더 번호 변경 작업을 자동화하면서 발전한 개인 프로젝트입니다.

## Current state

현재 루트에는 여러 버전의 Python 파일과 `build/`, `dist/` 같은 생성 산출물이 함께 존재합니다.

```text
changing_number/
├── README.md
├── docs/
│   └── README.md
├── source candidates (*.py)
├── *.spec
├── build/
└── dist/
```

## Recommended cleanup

다음 단계에서 실제 최신 실행 경로를 확인한 뒤 아래처럼 정리하는 것을 권장합니다.

```text
src/
├── main.py
├── ...

tests/
docs/
assets/

build/      # 가능하면 Git 추적 제외
 dist/      # 가능하면 Git 추적 제외
```

`123.py`, `456.py`, `debug2.py`, `final2.py`, `final3.py`, `fianl4.py`, `sik.py`처럼 개발 과정에서 생성된 파일은 **내용을 확인하기 전에는 삭제하지 않습니다.** 실제 최신 코드와 중복 여부를 확인한 후 보존할 것과 제거할 것을 구분해야 합니다.

## Portfolio principle

이 저장소에서 보여줄 핵심은 파일 개수가 아니라 **반복 업무를 발견하고 실제 사용 가능한 자동화 도구로 발전시킨 과정**입니다.
