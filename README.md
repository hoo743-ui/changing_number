# Changing Number

> **행정 업무에서 반복되는 파일·폴더 작업을 작은 GUI 도구로 자동화한 개인 프로젝트 모음**

**2025.07 — 현재 · 개인 · 지속 사용**  
`Python` `Tkinter` `pandas` `pypdf` `Automation`

## Overview

가천대학교 반도체사업단 근로장학생으로 업무하면서 반복적으로 발생하는 파일·폴더 처리 작업을 발견하고, 실제 사용자가 바로 사용할 수 있는 GUI 도구로 만들어왔습니다.

하나의 기능만 있는 프로젝트라기보다 **업무에서 발견한 작은 병목을 각각 도구로 해결한 자동화 Toolkit**에 가깝습니다.

## Tools

### 1. Folder Reorder Tool — `change.py`
폴더명을 `번호_이름` 형태로 관리하는 업무에서 순번을 자동으로 정렬합니다.

- 폴더 목록 자동 탐색
- Drag & Drop 지원
- 번호 중복 탐지
- 검색 / 필터
- 선택 폴더 삭제
- 휴지통 이동 및 복구
- 삭제 후 순번 자동 재정렬
- 잘못된 조작을 고려한 복구 경로

### 2. PDF Auto Splitter — `final3.py`
스캔 폴더에서 PDF를 감시하고, 학생 이름·학번을 입력해 정해진 문서 단위로 자동 분할합니다.

### 3. Excel ↔ Folder Matcher — `123.py`, `456.py`
Excel의 학생 이름과 실제 폴더 목록을 비교해 누락 여부를 확인하는 도구입니다.

### 4. PDF Page Replacement Tool — `sik.py`
여러 PDF에서 지정한 페이지를 다른 PDF의 지정 페이지로 교체하는 도구입니다.

## Why GUI?

이 도구들의 사용자는 개발자가 아니기 때문에 CLI보다 **업무 흐름에 맞는 GUI**를 우선했습니다.

특히 파일을 잘못 삭제하거나 순서를 잘못 변경했을 때 작업 전체를 다시 해야 하는 상황을 피하기 위해 휴지통·복구·중복 확인 같은 기능을 함께 고려했습니다.

## Current Use

**2025년 7월부터** 실제 업무에서 사용하기 위한 도구를 개발해왔으며, 현재도 업무 과정에서 필요한 기능을 추가하거나 예외를 수정하면서 **지속적으로 사용하고 있습니다.**

## Repository Structure

```text
changing_number/
├── README.md
├── docs/
│   └── README.md
├── change.py
├── final3.py
├── 123.py
├── 456.py
├── sik.py
└── change.spec
```

개발 과정에서 생성된 오래된 PDF splitter 버전과 진단용 debug script는 정리했습니다.

## Tech Stack

`Python` `Tkinter` `pandas` `pypdf / PyPDF2` `tkinterdnd2` `openpyxl` `PyInstaller`

## Context

가천대학교 반도체사업단 근로장학생으로 실제 행정 업무를 수행하면서 발견한 반복 작업을 개인적으로 자동화한 프로젝트입니다.

이 프로젝트에서 중요하게 본 것은 복잡한 알고리즘보다 **실제 사용자가 실수 없이 사용할 수 있는 도구를 만드는 것**이었습니다.

## What I Learned

작은 자동화라도 실제 업무에 적용하려면 기능 구현만으로 끝나지 않습니다.

**사용자의 작업 흐름 → 입력 오류 → 실패 상황 → 복구 방법 → 배포 가능한 형태**까지 함께 생각해야 한다는 것을 경험했습니다.
