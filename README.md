# 🌿 Token Garden

LLM 토큰 사용량을 터미널 정원으로 시각화하는 CLI 도구. GitHub 잔디처럼.

```
🌿 Token Garden — 2026

     JaJa      Fe      Ma      Ap      Ma      Ju
Mon  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Tue  ░░░░░░░░░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Wed  ░░░░░░░░░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Total 2026: 646,457 tokens  |  Peak: 2026-03-12 (438,662)
```

## 설치

### Homebrew

```bash
brew tap HongChaeMin/tap
brew install token-garden
```

### pip / pipx (지금 바로)

```bash
# pipx 권장 (격리된 환경)
pipx install token-garden

# 또는 pip
pip install token-garden
```

### 소스에서 직접

```bash
git clone https://github.com/hongchaemin/token-garden.git
cd token-garden
pip install -e .
```

## 사용법

### 1. 데이터 수집

```bash
token-garden sync
```

Claude Code 로그(`~/.claude/projects/`)를 파싱해서 토큰 사용량을 `~/.token-garden/db.sqlite`에 저장.

### 2. 정원 보기

```bash
# GitHub 잔디 스타일 (기본)
token-garden view

# 식물 성장 스타일
token-garden view --style garden

# 특정 연도
token-garden view --year 2025
```

## 뷰 종류

### Grid (기본)

GitHub 잔디와 동일한 52×7 그리드. 초록 진할수록 많이 사용.

| 색상 | 토큰 수 |
|------|---------|
| ░ | 0 |
| 🟩 (연) | 1 – 9,999 |
| 🟩 | 10,000 – 49,999 |
| 🟩 | 50,000 – 99,999 |
| 🟩 (진) | 100,000+ |

### Garden

주별 토큰 사용량을 식물로 표현.

| 식물 | 주간 토큰 수 |
|------|------------|
| (없음) | 0 |
| 🌱 | 1 – 9,999 |
| 🌿 | 10,000 – 49,999 |
| 🌲 | 50,000 – 99,999 |
| 🌳 | 100,000 – 199,999 |
| 🌴 | 200,000+ |

## 지원 모델

| Provider | 상태 | 데이터 소스 |
|----------|------|------------|
| Claude | ✅ | `~/.claude/projects/` 로컬 로그 |
| OpenAI | 🚧 준비중 | — |

## 데이터 저장 위치

- DB: `~/.token-garden/db.sqlite`

## 요구사항

- Python 3.11+
- Claude Code 사용 이력 (`~/.claude/projects/` 존재)
