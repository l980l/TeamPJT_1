# Render 배포 가이드

이 문서는 LocalHub 백엔드를 Render에 배포할 때 필요한 설정과 명령 예시를 정리합니다.

## 필수 환경변수
- `DATABASE_URL` 또는 `RENDER_DATABASE_URL` : PostgreSQL 연결 URL. (예: `postgresql://user:pass@host:5432/dbname`)
- `OPENAI_API_KEY` : OpenAI 기능을 사용하면 설정.
- `RUN_SEED_ON_STARTUP` (선택) : `true`/`1`/`yes`로 설정하면 앱 시작 시 DB가 비어있을 때 자동으로 `seed.py`를 실행합니다.

> 참고: 코드에서 `RENDER_DATABASE_URL`을 우선 읽고, 없으면 `DATABASE_URL`을 사용합니다.

## 권장 Start Command
Render 서비스의 Start Command에 아래 둘 중 하나를 사용하세요.

- 간단(개발/소형 서비스):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- 프로덕션(권장): Gunicorn + Uvicorn 워커

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

`gunicorn`을 사용하려면 `requirements.txt`에 `gunicorn`을 추가하세요.

## 시드(데이터 채우기)
- 자동 시드: `RUN_SEED_ON_STARTUP=true`를 환경변수로 설정하면 앱 시작 시 내부 로직이 DB가 비어있을 때 `seed.py`를 실행합니다.
- 수동 시드(원격 서버에서 한 번만 실행): Render의 one-off 쉘이나 CI에서 아래 명령 실행

```bash
# 환경변수가 설정된 상태에서
python seed.py
```

## 배포 순서(요약)
1. Render에 리포지토리 연결
2. Environment에 `DATABASE_URL` (또는 `RENDER_DATABASE_URL`), `OPENAI_API_KEY` 등 추가
3. Start Command 설정(위 예시 중 하나)
4. 재배포 후 로그에서 `DB connectivity OK` 또는 오류 메시지를 확인
5. 필요시 `RUN_SEED_ON_STARTUP=true`로 자동 시드하거나 수동으로 `python seed.py` 실행

## 헬스체크
배포 후 다음 엔드포인트로 DB 상태를 확인하세요:

- GET `/db_status` → `{ "ok": true, "items": <count>, "posts": <count> }`

---
문서를 더 다듬하거나 `Procfile`/CI 예시를 추가해드릴까요?
