# Docker 배포

## 빠른 시작

### 1. 이미지 빌드
```bash
docker build -t pdfocr:latest .
```

### 2. 사용 방법

#### 옵션 A: 직접 실행 (볼륨 마운트)
```bash
# 현재 디렉토리의 PDF 처리
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf

# 출력 디렉토리 지정
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf -o /work/output

# 여러 PDF 처리
docker run --rm -v $(pwd):/work pdfocr:latest *.pdf --merge
```

#### 옵션 B: Docker Compose 사용
```bash
# 기본 실행 (help 출력)
docker-compose run --rm pdfocr

# PDF 처리
docker-compose run --rm pdfocr document.pdf -o ./output

# 대화형 셸
docker-compose run --rm pdfocr /bin/bash
```

## 상세 사용 예시

### 단일 PDF 처리
```bash
# PDF 파일이 현재 디렉토리에 있을 때
docker run --rm -v $(pwd):/work pdfocr:latest ./lecture.pdf

# 절대 경로 사용
docker run --rm -v /home/user/documents:/work pdfocr:latest /work/document.pdf
```

### 일괄 처리
```bash
# 모든 PDF를 하나의 파일로 병합
docker run --rm -v $(pwd):/work pdfocr:latest ./*.pdf --merge -o ./output

# 각 PDF를 개별적으로 처리
docker run --rm -v $(pwd):/work pdfocr:latest ./pdfs/*.pdf -o ./output
```

### 고급 옵션
```bash
# 고해상도 (600 DPI)
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf --dpi 600

# 영어 OCR
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf --lang eng

# 이미지 보존
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf --keep-images -i ./images
```

## 볼륨 마운트 설명

Docker 컨테이너는 격리된 환경에서 실행되므로, 호스트의 파일에 접근하려면 볼륨을 마운트해야 합니다:

```bash
-v <호스트_경로>:<컨테이너_경로>
```

예시:
- `-v $(pwd):/work` - 현재 디렉토리를 `/work`에 마운트
- `-v /home/user/pdfs:/input` - 특정 폴더를 `/input`에 마운트

## Docker Compose 설정

`docker-compose.yml` 파일을 수정하여 기본 동작을 변경할 수 있습니다:

```yaml
version: '3.8'

services:
  pdfocr:
    build: .
    volumes:
      - ./input:/input      # 입력 폴더
      - ./output:/output    # 출력 폴더
    command: ["/input/document.pdf", "-o", "/output"]
```

사용:
```bash
docker-compose up
```

## 이미지 관리

### 이미지 빌드 및 태그
```bash
# 최신 버전으로 빌드
docker build -t pdfocr:latest .

# 특정 버전으로 빌드
docker build -t pdfocr:v0.0.1 .

# 멀티 태그
docker build -t pdfocr:latest -t pdfocr:v0.0.1 .
```

### 이미지 확인
```bash
# 빌드된 이미지 목록
docker images | grep pdfocr

# 이미지 상세 정보
docker inspect pdfocr:latest
```

### 이미지 정리
```bash
# 특정 이미지 삭제
docker rmi pdfocr:latest

# 사용하지 않는 이미지 전부 삭제
docker image prune -a
```

## 문제 해결

### 권한 문제
컨테이너가 생성한 파일의 소유자가 root일 수 있습니다:

```bash
# 사용자 ID로 실행
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/work pdfocr:latest document.pdf
```

### 한글 깨짐
로케일 설정이 올바른지 확인:
```bash
docker run --rm pdfocr:latest /bin/bash -c "locale"
```

출력에 `LANG=en_US.UTF-8`이 있어야 합니다.

### 메모리 부족
대용량 PDF 처리 시:
```bash
docker run --rm -m 4g -v $(pwd):/work pdfocr:latest large.pdf
```

### 로그 확인
```bash
# 컨테이너 로그 보기
docker logs <container_id>

# 디버그 모드로 실행
docker run --rm -v $(pwd):/work pdfocr:latest document.pdf -v
```

## 배포

### Docker Hub에 푸시
```bash
# 로그인
docker login

# 태그
docker tag pdfocr:latest username/pdfocr:latest
docker tag pdfocr:latest username/pdfocr:v0.0.1

# 푸시
docker push username/pdfocr:latest
docker push username/pdfocr:v0.0.1
```

### GitHub Container Registry
```bash
# 로그인
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 태그
docker tag pdfocr:latest ghcr.io/username/pdfocr:latest

# 푸시
docker push ghcr.io/username/pdfocr:latest
```

## 성능 최적화

### 멀티 스테이지 빌드
이미지 크기를 줄이려면 Dockerfile을 멀티 스테이지로 수정할 수 있습니다:

```dockerfile
# 빌드 단계
FROM ubuntu:22.04 AS builder
# ... 빌드 작업 ...

# 실행 단계
FROM ubuntu:22.04
COPY --from=builder /app /app
# ... 최소한의 런타임만 설치 ...
```

### 캐시 활용
빌드 속도를 높이려면:
```bash
# BuildKit 활성화
DOCKER_BUILDKIT=1 docker build -t pdfocr:latest .
```

## 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
