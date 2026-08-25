# Isaac Lab RL 셋업 가이드 — Isaac Sim 6.0.1 / Titan RTX

새 머신에서 아무것도 없는 상태에서 **cartpole PPO 학습이 실제로 도는 것**까지가 이 문서의 범위입니다.
개념·아키텍처(ManagerBased vs Direct, Term 구성, 커스텀 태스크)는 이 문서에 없습니다 — 학습이 한 번 돈 뒤에 별도 문서로 씁니다.

> **무엇을 왜 그 순서로 학습시키는가**는 [`docs/rl-operations-survey.md`](docs/rl-operations-survey.md)에 있습니다 — 착수 지점(부트스트랩 사다리), 평가 프로토콜, 승격 게이트, cable/cloth 산업 레퍼런스. 이 문서(설치·첫 학습)의 다음 층입니다.

## 표기 규칙

이 문서의 모든 주장에는 근거 등급이 붙습니다. **등급 없는 문장은 없습니다.**

| 표기 | 뜻 |
| --- | --- |
| `[실측]` | 작업 머신(RTX 4060 / Isaac Sim 6.0.1)에서 직접 확인한 값 |
| `[문서]` | NVIDIA 공식 문서·릴리스 노트 근거. 이 머신에서 실행해 본 것은 아님 |
| `[미확인]` | Titan 머신에서 확인해야 하는 것. **여기서 막히면 이 문서를 고칠 지점입니다** |

---

## 작업 흐름 — 소형 검증 → 대형 학습

두 머신을 씁니다.

| 머신 | 역할 |
| --- | --- |
| RTX 4060 (8GB) | **소형.** 코드가 도는지만 봅니다 |
| Titan RTX (24GB) | **대형.** 실제 학습 |

사이는 `git commit → push → pull`로 잇습니다.

### 양쪽 다 새로 깔아야 합니다

4060의 기존 conda 환경은 Python 3.11.15라 6.0.1을 못 씁니다 `[실측]`.
따라서 이 문서의 2·3절은 **Titan 전용이 아니라 양쪽에 적용됩니다.** 4060에 먼저 깔아 절차 자체를 검증하는 것이 소형 검증의 첫 항목입니다.

### 함정 — 개발 머신이 학습 머신보다 최신입니다

| | 4060 (소형/개발) | Titan RTX (대형/학습) |
| --- | --- | --- |
| 아키텍처 | Ada **sm_89** | Turing **sm_75** (두 세대 아래) |
| VRAM | 8GB | 24GB |
| bf16 | **있음** `[실측]` | **없음** |
| FP32 | ~15 TFLOPS | ~16 TFLOPS |
| 드라이버 | 591.86 `[실측]` | 591.86 `[실측]` — **같음** |
| 6.0 최소사양 | 미달 (VRAM) | 미달 (아키텍처) |

**4060은 Titan의 부분집합이 아닙니다.** VRAM만 작고 아키텍처는 오히려 최신입니다. 그래서 `소형 통과 → 대형 통과`가 성립하지 않습니다.

4060에서 통과하고 Titan에서 죽는 것들:

1. **bf16** — 4060에는 있고 `[실측]` Titan에는 없습니다. config에 `bf16`이 들어 있으면 소형은 조용히 통과하고 대형이 죽습니다
2. **Newton / Warp 커널** — `[문서]` Newton 공식 요구사항은 **Maxwell 이상, 드라이버 545 이상(CUDA 12)** 입니다. Turing(sm_75)은 범위 안이고 양쪽 드라이버가 591.86이므로 `[실측]` **이 항목의 위험도는 크게 내려갔습니다.** 다만 Warp는 아키텍처별로 커널을 컴파일하므로, 첫 실행에서 sm_75용 컴파일이 실제로 도는지는 Titan에서 봐야 합니다 `[미확인]`
3. **torch 빌드** — `[실측]` 설치된 torch는 **2.10.0+cu128**이고 arch 목록은 이렇습니다.

   ```
   ['sm_70', 'sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_100', 'sm_120']
   ```

   **`sm_75`가 들어 있습니다 — Titan 쪽 걱정은 해소됐습니다.** 그런데 예상과 반대로 **`sm_89`(4060)가 목록에 없습니다.** 그래도 `torch.cuda.is_available()`이 `True`이고 디바이스가 `NVIDIA GeForce RTX 4060`으로 잡힙니다 `[실측]` — 같은 major(8.x) 안에서는 하위 minor의 cubin이 상위에서 도는 CUDA 규칙 때문입니다 `[문서]`. 즉 4060은 `sm_86` 코드로, Titan은 `sm_75` 코드로 돌아갑니다. **이 항목은 위험 목록에서 빼도 됩니다**

### 그래서 검증을 이렇게 나눕니다

| 무엇을 검증하나 | 어디서 |
| --- | --- |
| 코드가 도는가 — 로직, 보상, 종료 조건, 저장 | **4060 소형** |
| 아키텍처 의존 — bf16, Warp 커널, torch arch | **Titan에서 먼저.** 소형으로 못 걸러집니다 |
| 스케일 — num_envs, VRAM, throughput | **Titan 대형** |

**결론: Titan을 마지막에 두지 마십시오.** Titan에 최소 설치를 먼저 하고 위 3개를 한 번 통과시켜 놓은 다음, 그때부터 4060 ↔ Titan 왕복을 시작하는 것이 맞습니다. 순서를 반대로 하면 4060에서 며칠 쌓은 것이 Titan 첫 실행에서 무너집니다.

### 8GB로는 소형 검증조차 안 되는 것

**카메라 기반 태스크** (`*-RGB-*`, `*-Depth-*`)는 렌더가 들어가 8GB에서 소형 검증이 안 될 수 있습니다 `[미확인]`.
이 부류는 왕복 대상이 아니라 **Titan 단독 개발**로 분류하십시오. 미리 갈라두면 헛된 왕복이 줄어듭니다.

### 디렉터리 배치 — Isaac Sim 설치 폴더 안에 넣지 마십시오

```
<드라이브>:\isaac_601\      Isaac Sim 6.0.1. 소모품 — 지우고 다시 풀 수 있게 비워둡니다
<드라이브>:\rl\
  IsaacLab\                 upstream 클론, v3.0.0-beta2 고정 (gitignore 대상)
  IsaacLabRL\               이 리포 — 가이드 + 태스크 코드
```

위는 **권장**이고 강제가 아닙니다. `[실측]` 실제 4060은 이렇게 되어 있습니다.

```
D:\IsaacLab\                3.0.0 체크아웃 — rl\ 옆이 아니라 드라이브 루트
D:\rl\IsaacLabRL\           이 리포
D:\simu\IsaacLab\           2.3.2 구 기준선
```

**이 차이는 문제가 아닙니다.** 확인한 근거는 두 가지입니다.

- `[실측]` 래퍼가 `<드라이브>:\IsaacLab`과 `<드라이브>:\rl\IsaacLab`을 **둘 다** 탐색합니다. 리포 어디에도 절대경로가 없으므로 체크아웃이 어디 있든 동작합니다
- `[실측]` 긴 경로 예산도 남습니다. 체크아웃 최장 경로가 **193자**이고 `rl\` 아래로 옮기면 196자입니다 — 260 한도까지 **64자 여유**. 게다가 이 머신은 `LongPathsEnabled=1`입니다. 즉 위치 선택이 경로 한도에 미치는 영향은 없습니다

그래서 **옮기지 않았습니다.** 옮기는 이득이 문서와 실제를 일치시키는 것뿐인데, 그건 문서를 실제에 맞추는 쪽이 쌉니다. 지금 이 문단이 그 처리입니다.

타이탄은 **단일 드라이브**라 `C:\` 아래가 됩니다 `[미확인]`. 위 목록과 드라이브 문자만 다르면 래퍼가 그대로 잡습니다. **어느 쪽을 잡았는지는 항상 `il --where`로 확인하십시오** — 체크아웃이 두 개라서 이게 유일한 확인 수단입니다.

중첩하면 안 되는 이유는 네 가지입니다.

1. **설치 폴더는 소모품입니다.** zip에서 푼 것이고 GA 빌드로 갈 때 깨끗한 방법은 지우고 다시 푸는 것입니다. 안에 있는 건 같이 죽습니다. 이미 `D:\isaac_601` 루트에 `baseline.csv`·`baseline.svg` 같은 작업 산출물이 섞여 있어 재설치가 위험해진 상태입니다 `[실측]`
2. **버전 커플링.** Sim 빌드가 둘 이상(rc / GA)일 때 같은 Isaac Lab 체크아웃을 양쪽에 대고 시험할 수 없습니다. `_isaac_sim` 링크의 존재 이유가 그 교체입니다
3. **두 머신 경로 대칭이 깨집니다.** 위의 "하드코딩 금지"를 디렉터리 구조로 위반하는 셈입니다
4. **긴 경로 예산.** `D:\rl\IsaacLab\`(15자)과 `D:\isaac_601\projects\IsaacLabRL\IsaacLab\`(42자)의 차이는 27자입니다. Isaac Lab 자체 경로가 이미 깊습니다

애초에 중첩이 필요 없는 이유는 **Isaac Lab에 Sim을 가리키는 전용 장치가 이미 있기 때문**입니다 — uv 경로면 pip 휠로 들어오고, 내려둔 설치를 쓰면 `_isaac_sim` 심링크입니다. 커플링을 위치가 아니라 링크로 표현합니다.

### 리포가 나르는 것과 나르지 않는 것

- **나릅니다** — 태스크 코드, config, 이 문서
- **안 나릅니다** — `logs/`, 체크포인트, tensorboard 이벤트 (`.gitignore`에 있음)
- **절대 하드코딩하지 마십시오** — 경로(`D:\isaac_601` 등), `num_envs`, device. 머신마다 달라지는 값은 CLI 인자나 config로 빼십시오. 하드코딩 하나가 pull 할 때마다 손으로 고치는 일을 만들고, 그게 이 왕복 흐름을 망가뜨리는 가장 흔한 원인입니다

### IsaacLab 커밋 고정은 선택이 아니라 필수입니다

`develop`은 움직입니다. 두 머신이 다른 날 clone하면 **다른 코드**가 됩니다 — beta 기간에는 며칠 단위로 실제로 벌어집니다. 그러면 "소형에서는 됐는데 대형에서 안 된다"의 원인이 내 코드인지 IsaacLab인지 구분이 불가능해집니다.

`[실측]` 4060의 체크아웃은 **브랜치**에 있습니다 — 태그가 아닙니다.

```
branch   release/3.0.0-beta2
commit   2e44ddb2e
describe v3.0.0-beta2.patch1-13-g2e44ddb2e
```

**`release/3.0.0-beta2`도 움직이는 브랜치입니다.** 이미 `v3.0.0-beta2.patch1` 태그에서 13 커밋 앞서 있습니다 `[실측]`. 그래서 타이탄에서 브랜치 이름으로 clone하면 **다른 코드가 됩니다.** 태그가 아니라 **커밋으로** 고정하십시오.

```bash
git clone https://github.com/isaac-sim/IsaacLab.git --branch release/3.0.0-beta2
```

```bash
git checkout 2e44ddb2e
```

| 머신 | IsaacLab 커밋 | Isaac Sim 빌드 | 드라이버 | 확인 날짜 |
| --- | --- | --- | --- | --- |
| 4060 (sm_89) | `2e44ddb2e` `[실측]` | **없음 — kitless** `[실측]` | 591.86 `[실측]` | 2026-08-20 |
| Titan (sm_75) | (채울 것 — 위 커밋에 맞추십시오) | (kitless면 없음) | 591.86 `[실측]` | (채울 것) |

`[실측]` 4060 쪽 검증 결과: torch 2.10.0+cu128 / warp 1.13.0 / cartpole PPO 10 iteration 통과. 4.3절.

`[실측]` **드라이버는 양쪽이 같습니다.** 그만큼 용의자가 하나 줄었습니다 — 아래 비대칭 표에서 남는 것은 아키텍처뿐입니다.

---

## 0. 대상 스택

| 구성 | 버전 | 근거 |
| --- | --- | --- |
| **설치 방식** | **kitless — Isaac Sim 없이 Newton만** | `[문서]` 3.0.0-beta2 kitless 문서. 3절 경로 C |
| Isaac Lab | **3.0.0 Beta 2** (`release/3.0.0-beta2` 브랜치) | `[문서]` kitless 문서가 이 브랜치를 지정 |
| Python | **3.12** | `[실측]` 체크아웃 venv가 3.12.4. `[문서]` Isaac Sim 6.X가 3.12 요구 |
| **물리 엔진** | **Newton** — `physics=newton_mjwarp` | `[실측]` 체크아웃에 `source/isaaclab_newton` 존재. `physics=`는 hydra 타입 셀렉터 |
| Isaac Sim | **불필요.** RTX 렌더가 필요해지면 6.0.1 | `[문서]` kitless는 Isaac Sim을 요구하지 않습니다 |
| RL 라이브러리 | `rsl_rl` | 기본. rl_games/skrl/sb3는 별도 설치 |
| 패키지 관리 | **uv** | `[문서]` 3.0 문서의 권장 경로. conda 아님 |

**Newton으로 확정했습니다.** 이유는 세 가지입니다.

1. `[문서]` **Maxwell 이상**을 지원하므로 Titan RTX(sm_75)가 범위 안입니다. 위 함정 표의 2번 항목이 여기서 대부분 해소됩니다
2. `[문서]` **kitless로 갈 수 있습니다** — Isaac Sim 설치가 아예 빠지므로 6.0.1 rc/GA 문제, `_isaac_sim` 심링크, 관리자 권한 `mklink`, 8GB VRAM 최소사양이 전부 사라집니다
3. `[문서]` Newton 리포에 40개 이상의 예제가 있고 매니퓰레이터·컨베이어·강체 조립 쪽이 이 프로젝트가 하려는 것과 겹칩니다

**대신 포기하는 것이 있습니다.** 3절 경로 C의 표를 먼저 보십시오 — 특히 **PhysX 폴백이 없어집니다.**

### 버려지는 것

기존 작업 머신에는 conda 환경 `env_isaaclab`(Isaac Sim 5.1.0.0 + Isaac Lab 2.3.2 + torch 2.7.0+cu128 + rsl_rl 5.0.1)이 깔려 있고 패키지 정합성은 정상입니다 `[실측]`.
그런데 **Isaac Lab 2.3은 Isaac Sim 6.0과 호환되지 않습니다** `[문서]`. 6.0.1로 가는 순간 이 환경은 재사용 대상이 아니라 참조 대상입니다.

결정적으로, 그 conda 환경은 **Python 3.11.15**입니다 `[실측]`. Isaac Sim 6.0은 3.12를 요구하므로 `[문서]` **제자리 업그레이드가 불가능합니다** — 인터프리터부터 다릅니다. 새 환경이 유일한 경로입니다.

- 옮겨오는 것: 없음. 새로 깝니다
- 남겨두는 이유: 3.0 beta에서 막혔을 때 비교할 기준선이 됩니다. 지우지 마십시오
- 주의: 그 환경도 **학습을 한 번도 돌린 적이 없습니다** `[실측]` (`logs/` 부재). "돌아가는 환경"이 아니라 "설치가 끝난 환경"입니다

#### 이름이 겹칩니다 — `env_isaaclab`이 두 개입니다 `[실측]`

| 무엇 | 위치 | Python |
| --- | --- | --- |
| **conda** 환경 (구, 2.3.2용) | `%USERPROFILE%\miniconda3\envs\env_isaaclab` | **3.11.15** — 6.0에 못 씁니다 |
| **uv venv** (신, 3.0용) | `D:\rl\IsaacLabRL\env_isaaclab` | **3.12.4** |

**이름이 같고 내용이 다릅니다.** 프롬프트에 `(env_isaaclab)`만 보이면 어느 쪽인지 구분이 안 됩니다. 손이 기억하는 `conda activate env_isaaclab`을 치면 3.11.15가 잡히고, 그 다음부터 나오는 에러는 원인이 전혀 안 보이는 종류가 됩니다.

**래퍼가 이걸 막습니다** `[실측]`. `il.bat`은 conda가 활성이든 아니든 `<리포>\env_isaaclab`을 찾아 `VIRTUAL_ENV`로 못 박고, conda가 같이 켜져 있으면 경고를 냅니다. 그래도 원칙은 그대로입니다 — **conda는 끄고 쓰십시오.**

#### IsaacLab 체크아웃도 두 개입니다 `[실측]`

| 버전 | 위치 | 용도 |
| --- | --- | --- |
| **2.3.2** | `D:\simu\IsaacLab` | 구 기준선. 지우지 마십시오 |
| **3.0.0** | `D:\IsaacLab` | 이 문서의 대상 |

래퍼의 탐색 경로에 `D:\simu\IsaacLab`은 들어 있지 않으므로 섞일 위험은 없습니다. `il --where`로 어느 쪽을 잡았는지 매번 확인할 수 있습니다.

### Isaac Lab 3.0이 beta라는 사실의 의미

`[문서]` 2.x에서 3.0은 메이저 버전 횡단이고 다음이 바뀌었습니다.

- 일부 **manager API가 제거**되었습니다
- **Newton 초기화 방식**이 달라졌습니다
- **math 모듈을 쓰지 않는 커스텀 MDP는 깨집니다**
- Direct RL 태스크에 **CUDA graph 지원**이 들어와 오버헤드가 줄었습니다 (이건 이득)

즉 인터넷에서 찾는 2.x 기준 예제·튜토리얼은 **대부분 그대로 안 됩니다.** 검색 결과를 붙여넣기 전에 그게 2.x인지 3.0인지 먼저 보십시오. 이 문서에서 가장 시간을 잡아먹을 항목입니다.

---

## 1. Titan RTX 판정 — 먼저 읽으십시오

`[문서]` Isaac Sim 6.0의 공식 최소 사양입니다.

| 항목 | 최소 사양 | Titan RTX | 판정 |
| --- | --- | --- | --- |
| GPU | GeForce RTX 4080 | Titan RTX (Turing, sm_75) | **미달** — 두 세대 아래 |
| VRAM | 16GB | 24GB | 충족 |
| 드라이버 (Windows) | **581.42** | **591.86** | 충족 `[실측]` |
| RT Core | 필수 (A100/H100 미지원) | 있음 | 충족 |

즉 **미달은 아키텍처 한 항목뿐입니다.** VRAM·드라이버·RT Core는 다 통과합니다.

### 이 미달을 어떻게 읽어야 하는가

**돌 가능성이 높습니다.** 16GB / "16MP per frame" 요구는 문서 문맥상 **렌더링** 기준이고, 헤드리스 RL 학습은 렌더를 하지 않습니다. RT Core가 있어 명시적 미지원 아키텍처(A100/H100) 범주도 아닙니다.

위험이 실제로 나타나는 곳은 세 군데입니다.

1. **GUI 확인** — 정책을 뷰포트로 눈으로 볼 때
2. **카메라 기반 태스크** — `*-RGB-*`, `*-Depth-*`. 렌더가 들어가므로 여기서 미달이 직접 물립니다
3. **지원** — 최소 사양 미달 구성은 NVIDIA 포럼에서 답을 받기 어렵습니다

### 성능 기대치를 정확히 잡으십시오

| | RTX 4060 (기존) | Titan RTX (신규) |
| --- | --- | --- |
| VRAM | 8GB | **24GB** (3배) |
| FP32 | ~15 TFLOPS | ~16 TFLOPS (거의 동일) |
| bf16 | 지원 (Ada) | **없음** (Ampere/sm_80 이상 필요) |

**3배 넓어지는 것이지 3배 빨라지는 게 아닙니다.** 연산량이 거의 같습니다.
실제 학습 속도 개선은 "env 수를 올릴 수 있다 → GPU 물리 시뮬레이션 throughput이 올라간다"에서 나오고, env 하나당 스텝 시간은 비슷합니다.

**bf16이 없는 것은 별도 함정입니다.** AMP를 bf16으로 켜는 설정을 만나면 fallback되거나 죽습니다. fp32 또는 fp16으로 가야 합니다. 학습 config에서 `bf16` / `bfloat16` 문자열을 grep해 두십시오.

### 드라이버

확인은 끝났습니다. 재확인이 필요할 때(드라이버 업데이트 후 등) 쓰는 명령입니다.

```bash
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv
```

581.42 이상이면 통과입니다.

`[실측]` **두 머신 모두 591.86입니다** (Titan, 4060 동일. 2026-01-20 빌드). 통과입니다.

이 값이 두 가지를 확인해 줍니다.

1. **Turing은 아직 드라이버를 받습니다.** Titan RTX(Turing)에 591.86이 올라가 있다는 것은 R590 브랜치가 Turing을 계속 지원한다는 직접 증거입니다 — Maxwell/Pascal/Volta가 R580에서 끊긴 것과 다릅니다. 추정이 아니라 실측입니다
2. **드라이버는 두 머신 사이의 변수가 아닙니다.** 왕복 흐름에서 "소형에서 됐는데 대형에서 안 된다"가 나올 때 드라이버는 용의자에서 제외됩니다. 남는 비대칭은 **아키텍처 하나뿐**입니다 (sm_89 vs sm_75)

#### 함정 — 장치 관리자의 버전은 다르게 생겼습니다

Windows 장치 관리자와 드라이버 속성창은 **WDDM 버전**을 보여줍니다. NVIDIA 문서와 `nvidia-smi`가 쓰는 릴리스 번호와 형태가 전혀 다릅니다.

| 어디서 보는가 | 표기 |
| --- | --- |
| 장치 관리자 / 드라이버 속성 | `32.0.15.9186` |
| `nvidia-smi`, NVIDIA 문서 | `591.86` |

**변환 규칙:** 점을 무시하고 **끝 5자리**를 떼어 마지막 두 자리 앞에 소수점을 넣습니다.

```
32.0.15.9186  →  ...5 9186  →  59186  →  591.86
```

`32.0.15.8142` 같은 값이면 `581.42`가 되어 최소 사양과 정확히 같습니다.

`[실측]` `32.0.15.9186`(2026-01-20 빌드) = **591.86** 이고, 최소 사양 581.42를 넘습니다.

**최소 사양과 비교할 때는 반드시 `nvidia-smi` 값으로 하십시오.** `32.0.15.9186`을 `581.42`와 직접 비교하면 대소를 잘못 읽습니다 — 앞자리 `32`가 작아 보여 미달로 오판하기 쉽습니다.

---

## 2. Windows 사전 준비

### 2.0 사전 점검 스크립트를 먼저 돌리십시오

[check_env.py](check_env.py)가 이 절과 1절의 확인 항목을 자동으로 봅니다. **Isaac Sim을 부팅하지 않고**, torch가 없어도 돕니다. 필수 항목이 실패하면 non-zero로 끝납니다.

```bash
python check_env.py
```

보는 것: Python 3.12 여부, 드라이버 581.42 통과, VRAM, compute capability로부터 bf16 지원 여부, (torch가 있으면) CUDA 가용성과 **이 torch 빌드가 해당 GPU arch용 커널을 실제로 갖고 있는지**.

마지막 항목이 Titan에서 중요합니다. sm_75용 커널이 없는 torch 빌드를 만나면 학습 도중이 아니라 여기서 터집니다.

`[실측]` 이 스크립트는 기존 머신에서 두 경로 모두 검증했습니다 — Python 3.12 + torch 미설치에서 통과(exit 0), Python 3.11.15 + torch 2.7.0+cu128에서 Python 실패 검출(exit 1).

### 2.1 긴 경로 지원 — 건너뛰면 설치가 깨집니다

`[문서]` **관리자 PowerShell**에서 실행합니다.

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
```

Isaac Lab / Isaac Sim의 익스텐션 경로가 260자를 넘습니다. 이걸 안 하면 clone이나 설치 중간에 원인이 불분명한 파일 없음 에러로 죽습니다. **실행 후 재부팅하십시오.**

### 2.2 나머지

- **Python 3.12** — uv 경로를 쓰면 uv가 잡습니다. 시스템에 따로 깔 필요는 없습니다
- **git**
- **디스크** — Isaac Sim 본체만 수십 GB입니다. 설치 드라이브 여유를 먼저 확인하십시오

---

## 3. 설치

세 경로가 있습니다. **Newton만 쓸 거면 C(kitless)가 가장 짧고, 이 프로젝트의 선택입니다.** Isaac Sim의 RTX 렌더나 PhysX가 필요하면 A(uv 자동) 또는 B(내려둔 Sim 사용)입니다.

### 경로 C — kitless: Isaac Sim 없이 Newton만 `[문서]` ← 이 프로젝트의 선택

Isaac Lab을 **Isaac Sim 없이** 설치합니다. 단계가 가장 적고, Newton만 쓸 거면 이것으로 충분합니다.

```bash
git clone https://github.com/isaac-sim/IsaacLab.git --branch release/3.0.0-beta2
```

```powershell
uv venv --python 3.12 --seed env_isaaclab
```

```powershell
env_isaaclab\Scripts\activate
```

```powershell
.\il.bat -i
```

#### uv가 PATH에 없었습니다 `[실측]`

`uv`는 `%USERPROFILE%\.local\bin\uv.exe`에 0.12.5로 깔려 있는데 **PATH에는 없습니다** `[실측]`. 그리고 `--install`은 uv를 먼저 찾고, 못 찾으면 **조용히 pip으로 내려갑니다** `[실측]`. 그대로 두면 같은 리포가 두 머신에서 서로 다른 방식으로 설치됩니다 — 나중에 원인 추적이 안 되는 종류의 차이입니다.

`il.bat`이 이것도 맞춰 줍니다. uv가 PATH에 없고 `%USERPROFILE%\.local\bin\uv.exe`가 있으면 PATH 앞에 붙이고, 그렇게 했다는 것을 출력합니다.

```
[il] uv       : put C:\Users\<사용자>\.local\bin on PATH
```

`[실측]` 자식 프로세스에서 실제로 잡히는 것까지 확인했습니다 — `shutil.which("uv")`가 `%USERPROFILE%\.local\bin\uv.EXE`를 돌려줍니다.

**공식 문서는 venv를 IsaacLab 클론 안에 만들라고 합니다** `[문서]`. 이 머신은 리포 쪽(`D:\rl\IsaacLabRL\env_isaaclab`)에 있습니다 `[실측]` — 위치가 다릅니다. `--install`은 활성 `VIRTUAL_ENV`에 설치하므로 결과는 같고 `[실측]`, `il.bat`이 그 `VIRTUAL_ENV`를 못 박아 줍니다. 아래 래퍼 절을 보십시오.

#### `il -i`가 실제로 설치하는 것 `[실측]`

체크아웃의 `source/isaaclab/isaaclab/cli/commands/install.py`를 읽고 확인한 것입니다.

- core 서브모듈 전부 + optional(`mimic`, `teleop`)
- extra feature 중 `newton`, `rl`, `visualizer` — `contrib`와 `ov`는 수동 대상이라 빠집니다
- **`isaacsim` 휠은 들어오지 않습니다.** `-i isaacsim`을 명시할 때만 들어옵니다 — **kitless가 성립하는 지점이 여기입니다**
- 패키지 인덱스로 `pypi.nvidia.com`, find-links로 `py.mujoco.org`를 씁니다. 네트워크가 필요합니다

더 줄이려면 토큰을 직접 주십시오 — kitless에서 못 쓰는 `teleop`/`mimic`이 빠집니다.

```powershell
.\il.bat -i newton,rl[rsl-rl],visualizer[newton]
```

첫 통과를 노릴 때는 `-i`(=all)를 권합니다. 변수가 적습니다.

#### kitless에서 포기하는 것 `[문서]`

| 되는 것 | 안 되는 것 |
| --- | --- |
| Newton 물리 — MuJoCo-Warp 솔버 포함 | **PhysX 백엔드** — Isaac Sim 필요 |
| Newton visualizer | Isaac Sim RTX 렌더, Kit visualizer |
| `ovphysx`·`ovrtx` 백엔드 — `-i ov[...]` | URDF/MJCF GUI 임포터 |
| | teleoperation·imitation learning 워크플로 |
| | PhysX deformable |

**이 프로젝트에 실제로 걸리는 것은 두 가지입니다.**

1. **PhysX 폴백이 없습니다.** 4.2절의 "Newton이 막히면 PhysX로 내려서 원인을 분리한다"가 kitless에서는 불가능합니다. Newton에서 막히면 그 자리에서 뚫어야 합니다
2. **카메라 기반 태스크가 빠집니다.** RTX 렌더가 없으므로 `*-RGB-*`·`*-Depth-*`는 kitless 대상이 아닙니다. 위 "8GB로는 소형 검증조차 안 되는 것" 절에서 Titan 단독으로 분류한 그 부류가 kitless에서는 **양쪽 다 불가**입니다 — 필요해지면 경로 A/B로 Isaac Sim을 붙여야 합니다

GUI 임포터가 빠지는 것은 기존 USD/STEP 자산을 올릴 때 걸릴 수 있습니다 `[미확인]`. Newton이 OpenUSD를 읽는 것은 `[문서]`로 확인됐지만, 변환 파이프라인이 따로 필요한지는 자산을 실제로 올려 봐야 압니다.

### 경로 A — uv 자동 셋업 (Isaac Sim 포함) `[문서]`

Isaac Sim까지 uv가 받아옵니다. 단계가 가장 적습니다.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
git clone https://github.com/isaac-sim/IsaacLab.git --branch develop
```

그 다음 `IsaacLab` 폴더에서 학습을 바로 부릅니다 — uv가 첫 실행 때 환경을 구성합니다.

```bash
uv run isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct physics=newton_mjwarp
```

**주의할 점 세 가지**

- `develop` 브랜치입니다. 재현성이 필요하면 clone 후 `git checkout v3.0.0-beta2`로 태그에 고정하십시오. `develop`은 움직입니다
- **CLI가 2.x와 완전히 다릅니다.** 2.x의 `scripts/reinforcement_learning/rsl_rl/train.py`가 아니라 `isaaclab train` 서브커맨드입니다. `physics=newton_mjwarp`는 Hydra 스타일 오버라이드로 보입니다
- 위 명령은 `[문서]`이고 이 머신에서 실행해 본 것이 아닙니다. **첫 실행 전에 공식 설치 문서와 대조하십시오** (아래 링크). beta라 명령 형태가 바뀔 수 있습니다

### 경로 B — 이미 내려둔 Isaac Sim 사용 `[문서]`

Isaac Sim 6.0.1 압축을 이미 풀어놨다면 재다운로드(수십 GB)를 피할 수 있습니다.
기존 작업 머신에는 `D:\isaac_601`에 풀려 있습니다 `[실측]`.

```cmd
set ISAACSIM_PATH=D:\isaac_601
```

```cmd
set ISAACSIM_PYTHON_EXE=%ISAACSIM_PATH%\python.bat
```

먼저 Isaac Sim 자체가 뜨는지 확인합니다. 첫 부팅은 셰이더·익스텐션 캐시 때문에 수 분 걸립니다 — 멈춘 것처럼 보여도 정상입니다.

```cmd
%ISAACSIM_PATH%\isaac-sim.bat
```

```cmd
%ISAACSIM_PYTHON_EXE% -c "print('Isaac Sim configuration is now complete.')"
```

그 다음 Isaac Lab을 붙입니다. `mklink`는 **관리자 권한**이 필요합니다.

```bash
git clone https://github.com/isaac-sim/IsaacLab.git --branch develop
```

```cmd
mklink /D _isaac_sim %ISAACSIM_PATH%
```

```cmd
isaaclab.bat -i
```

설치 확인 — 빈 씬이 뜨면 통과입니다.

```cmd
isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py --viz kit
```

**경로 B의 함정** — 기존 머신 `D:\isaac_601`의 VERSION은 `6.0.1-rc.7+release.42383`입니다 `[실측]`. **GA가 아니라 rc 빌드입니다.** Isaac Lab 3.0 Beta 2는 6.0.1을 타깃하는데 rc와 GA가 다르게 동작할 수 있습니다. Titan 머신에는 가능하면 **GA 빌드를 새로 받으십시오.** 설치 후 `VERSION` 파일에 rc 표기가 있는지 확인하십시오.

### 래퍼 — 경로를 매번 맞추지 않기 `[실측]`

**리포와 IsaacLab 체크아웃은 별개의 위치입니다.** `[실측]` 이 머신은 리포가 `D:\rl\IsaacLabRL`, 체크아웃이 `D:\IsaacLab`입니다 — 위에서 권장한 `D:\rl\IsaacLab`과도 다릅니다.

`isaaclab.bat`을 직접 부르면 셸을 체크아웃 폴더로 옮기게 되고, 그러면 두 가지가 어긋납니다.

1. **`logs/`가 체크아웃 안에 생깁니다.** 체크아웃은 gitignore 대상이고 지우고 다시 clone하는 소모품입니다 — 학습 산출물이 거기 쌓이는 것은 사고입니다. `logs/rsl_rl/...`는 **cwd 기준 상대경로**입니다
2. **어느 python이 잡히는지 흐려집니다.** `isaaclab.bat`은 `VIRTUAL_ENV` → `CONDA_PREFIX` → `_isaac_sim\python.bat` 순으로 찾습니다. 셸 상태에 따라 답이 바뀝니다

그래서 리포 루트에 래퍼를 두었습니다. **cwd를 옮기지 않고** 경로만 맞춥니다.

| 파일 | 하는 일 |
| --- | --- |
| `il.bat` | `isaaclab.bat` 전체를 감쌉니다. 인자를 그대로 넘깁니다 |
| `train.bat` | `il train --rl_library rsl_rl` + **Newton 기본값** |
| `play.bat` | `il play --rl_library rsl_rl` + Newton 기본값 + visualizer |
| `smoke.bat` | kitless 문서의 검증 명령 그대로. 4.1절 |
| `_rlargs.bat` | 내부용. 기본값 주입 판단만 합니다 |
| `isaaclab.local.bat.example` | 머신별 override 틀 |

리포 루트에서, 셸을 옮기지 않고 부릅니다.

```powershell
.\smoke.bat
```

```powershell
.\train.bat --task=Isaac-Cartpole-Direct-v0 --num_envs=1024 --headless
```

```powershell
.\il.bat -i
```

```powershell
.\il.bat -p scripts\tutorials\00_sim\create_empty.py --viz kit
```

경로가 어떻게 잡혔는지만 보려면:

```powershell
.\il.bat --where
```

`[실측]` 이 머신에서의 출력입니다.

```
[il] IsaacLab : D:\IsaacLab
[il] venv     : D:\rl\IsaacLabRL\env_isaaclab
[il] cwd      : D:\rl\IsaacLabRL
```

#### 무엇을 어떤 순서로 찾는가

**IsaacLab 체크아웃** — 먼저 맞는 것을 씁니다. `isaaclab.bat`의 존재로 판정합니다.

1. 환경변수 `ISAACLAB_PATH`
2. `<리포>\IsaacLab` — 리포 안에 둔 경우
3. `<리포>\..\IsaacLab` — 권장 배치
4. `<드라이브>:\rl\IsaacLab`
5. `<드라이브>:\IsaacLab` — `[실측]` 이 머신이 여기서 잡힙니다
6. `%USERPROFILE%\IsaacLab`

**python 환경** — `Scripts\python.exe`의 존재로 판정하고, 찾으면 `VIRTUAL_ENV`를 못 박습니다.

1. 환경변수 `ISAACLAB_VENV`
2. 이미 활성화된 `VIRTUAL_ENV`
3. `<리포>\env_isaaclab` — `[실측]` 이 머신이 여기서 잡힙니다
4. `<리포>\.venv`
5. `<체크아웃>\.venv` — uv 경로
6. 없으면 `isaaclab.bat`의 폴백에 맡기고 경고만 냅니다

**uv** — PATH에 없으면 `%USERPROFILE%\.local\bin`을 앞에 붙입니다. 3절의 "uv가 PATH에 없었습니다"를 보십시오.

conda가 활성 상태인데 venv도 찾으면 **venv를 쓰고 경고를 냅니다.** 5.2의 "섞지 마십시오"를 래퍼 수준에서 한 번 더 막는 것입니다.

#### Newton 기본값 주입

`train.bat`·`play.bat`은 `physics=newton_mjwarp`를 **자동으로 붙입니다.** 매번 손으로 쓰지 않기 위한 것이고, 이 프로젝트가 Newton으로 확정됐기 때문입니다.

**직접 준 것이 있으면 붙이지 않습니다.** `[실측]` 아래는 전부 실행해서 확인한 것입니다.

| 부른 것 | 실제로 넘어가는 것 |
| --- | --- |
| `train --task=X --num_envs=16` | `--task=X --num_envs=16 physics=newton_mjwarp` |
| `train --task=X physics=physx` | `--task=X physics=physx` — 주입 없음 |
| `train --task=X presets=inference` | `--task=X presets=inference` — 주입 없음 |
| `play --task=X` | `--task=X physics=newton_mjwarp --visualizer=newton` |
| `play --task=X --headless` | `--task=X --headless physics=newton_mjwarp` — viz 없음 |
| `play --task=X --viz none` | `--task=X --viz none physics=newton_mjwarp` |

끄는 방법은 **`off`** 입니다. 변수를 지우는 것으로는 안 꺼집니다 — 지우면 래퍼가 기본값을 다시 넣습니다.

```powershell
$env:IL_PHYSICS="off"
```

학습 중에도 Newton 뷰어를 보고 싶으면 켜십시오. `play`는 기본으로 켜져 있습니다.

```powershell
$env:IL_VISUALIZER="newton"
```

`--visualizer`는 `--viz` 별칭에 CSV를 받습니다 — `kit,newton,rerun,viser`, 끄려면 `none` `[실측]`. `none`은 Isaac Lab의 실제 값이라 센티넬로 쓰지 않고, 그래서 주입을 끄는 값은 `off`입니다.

#### 두 가지 함정 — 둘 다 실제로 밟았습니다

**1. `train.bat train ...` 처럼 쓰지 마십시오.** `train.bat` 자체가 이미 `train`입니다. 앞에 `train`을 또 쓰면 `--rl_library rsl_rl train --task ...`가 되는데, argparse가 조용히 무시하기 때문에 **틀린 채로 도는 것처럼 보입니다.** 지금은 래퍼가 막고 고칠 방법을 알려줍니다 `[실측]`.

**2. `.bat`에 한글을 넣지 마십시오.** `[실측]` cmd는 `.bat`을 콘솔 OEM 코드페이지(여기서는 949)로 읽습니다. UTF-8 한글을 넣으면 바이트가 어긋나 이런 것이 나옵니다.

```
'덈떎.'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는
배치 파일이 아닙니다.
```

주석이 실행되는 것처럼 보이는 이 증상이 그것입니다. **래퍼 파일은 전부 ASCII로 고정했습니다.** 한글 설명은 이 문서에만 둡니다 — 편집기는 UTF-8로 읽으니 문제가 없습니다. 래퍼를 고칠 때 이 규칙을 깨지 마십시오. 타이탄 머신의 코드페이지가 다르면 증상만 달라지고 원인은 같습니다.

#### 자동 탐색이 실패하면

이 여섯 곳에 없으면 래퍼가 찾아본 경로를 전부 출력하고 exit 2로 죽습니다. 그때만 머신별 override를 만드십시오.

```cmd
copy isaaclab.local.bat.example isaaclab.local.bat
```

`isaaclab.local.bat`은 gitignore 대상입니다. **절대경로가 들어가도 되는 파일은 이것뿐입니다** — 리포의 다른 파일에는 쓰지 마십시오. 타이탄에서 드라이브 문자만 다르면 위 4·5번이 알아서 잡으므로 이 파일 자체가 필요 없을 가능성이 높습니다 `[미확인]`.

#### 지금 상태에서 확인된 것과 안 된 것

**확인된 것** `[실측]`

- 체크아웃(`D:\IsaacLab`)과 venv(`<리포>\env_isaaclab`) 자동 탐색
- 인자 전달, Newton 기본값 주입 6가지 경우, 종료코드 전파(설정 오류 2 / 실행 실패 1)
- cwd가 체크아웃 안일 때 경고, conda 동시 활성 시 경고
- CP949 콘솔에서 깨진 출력 없음
- uv를 PATH에 올려 자식 프로세스가 잡는 것

**끝까지 확인됐습니다** `[실측]` 2026-08-20

`il -i` 설치가 에러 0으로 끝나고(venv 5.82 GB / 178 패키지), `smoke.bat`이 체크포인트까지 갔습니다. 4.3절을 보십시오. 래퍼는 이제 "동작이 확인된" 상태이고 **학습 경로 전체가 `[실측]`** 입니다.

설치를 다시 할 때 conda base는 빼십시오 — 프롬프트가 `(base) (env_isaaclab)`이면 둘이 겹친 상태입니다.

```powershell
conda deactivate
```

---

## 4. 첫 학습

목표는 **좋은 정책이 아니라 파이프라인이 끝까지 도는 것**입니다. cartpole은 몇 분 안에 풉니다.

### 4.1 smoke 먼저

kitless 문서의 검증 명령을 `smoke.bat`에 그대로 옮겨 놨습니다 — 16 envs / 10 iteration이라 몇 분입니다.

```powershell
.\smoke.bat
```

통과하면 본 학습입니다. `physics=newton_mjwarp`는 래퍼가 넣어 줍니다.

```powershell
.\train.bat --task=Isaac-Cartpole-Direct-v0 --num_envs=1024 --headless
```

`[실측]` 태스크 ID는 `Isaac-Cartpole-Direct-v0`입니다 — 체크아웃의 `direct/cartpole/__init__.py`에서 확인했습니다. 접미사 없이 `Isaac-Cartpole-Direct`로 불러도 gymnasium이 최신 버전을 골라 주지만, 이 문서에는 확정된 ID를 씁니다.

`[실측]` 위 한 줄이 실제로 실행하는 것 — `il.bat --where`와 같은 방식으로 확인했습니다.

```
isaaclab.bat train --rl_library rsl_rl --task=Isaac-Cartpole-Direct-v0 --num_envs=1024 --headless physics=newton_mjwarp
```

### 4.2 PhysX로 (Newton이 막히면)

**kitless(경로 C)에서는 이 절을 쓸 수 없습니다.** PhysX 백엔드가 Isaac Sim 안에 있기 때문입니다 `[문서]`. 아래는 경로 A/B로 설치한 경우의 이야기입니다.

`[문서]` Isaac Lab 3.0은 Newton과 PhysX **양쪽**을 지원합니다. Newton은 Warp 기반이라 Turing(sm_75)에서의 검증 사례가 적습니다 `[미확인]`.
Newton에서 커널 컴파일이나 아키텍처 관련 에러가 나면 **PhysX로 내려서 먼저 학습을 돌려 보십시오.** 원인 분리가 됩니다 — 파이프라인 문제인가, Newton 문제인가.

`physics` 오버라이드에 들어갈 PhysX 값은 `--help`나 문서에서 확인하십시오. **이 문서에 추측값을 적지 않습니다.**

### 4.3 성공 판정 — 통과했습니다 `[실측]` 2026-08-20

**4060에서 Newton으로 cartpole PPO가 끝까지 돌았습니다.** 이 리포에서 학습이 돈 첫 기록입니다 — 그전까지 `logs/`는 존재하지 않았습니다.

```
logs\rsl_rl\cartpole_direct\2026-08-20_11-49-48\
  model_0.pt                    45 KB
  model_9.pt                    45 KB
  events.out.tfevents...         7 KB
  params\agent.yaml, env.yaml
  git\IsaacLab.diff
```

- **체크포인트가 리포 안에 생겼습니다.** `D:\rl\IsaacLabRL\logs\...` — 체크아웃이 아닙니다. 래퍼가 cwd를 안 옮기는 설계가 여기서 값을 합니다
- reward가 **-4.07 → 8.28**로 올랐습니다 (10 iteration). 이 단계 목표는 아니었지만 학습 자체가 도는 것도 같이 확인됐습니다
- 실험 이름은 `cartpole_direct`입니다

#### 시작 비용이 학습 시간보다 20배 큽니다 `[실측]`

| 단계 | 시간 |
| --- | --- |
| Finalize builder | 1.1초 |
| **Initialize solver** | **33.5초** |
| **CUDA graph** | **32.9초** |
| 학습 10 iteration | **10.05초** (iteration당 0.36~0.37초, 첫 회만 1.77초) |

**시작에 약 66초, 학습에 10초입니다.** 첫 실행에서 로그가 40초쯤 멈춰 보이는 것이 이 구간입니다 — 죽은 게 아닙니다. 5.4절과 직접 이어집니다: **벽시계 시간으로 속도를 비교하면 안 됩니다.** 짧은 실행에서는 측정값이 거의 전부 solver init과 CUDA graph 비용입니다.

#### 무해한 것 — 쫓지 마십시오 `[실측]`

첫 실행 로그에 나오지만 학습에 영향이 없는 것들입니다.

- `Exception ignored on calling ctypes callback function: Win32Window...  _event_killfocus` — pyglet 뷰어 창의 포커스 콜백입니다. **뷰어가 떴다는 증거**이고, `Exception ignored`라 그대로 진행됩니다
- `Warning: The rigid body at .../slider has a possibly invalid inertia tensor ... negative mass` — cartpole 자산 자체의 경고입니다. cart/pole도 같은 경고가 납니다
- `FutureWarning: Newton shape color replacement is enabled` — deprecation 예고입니다
- `Failed to get root com velocity. If the articulation is fixed, this is expected.` — 메시지 자체가 정상이라고 말합니다
- `IO descriptors are only supported for manager based RL environments` — Direct 환경이라 그렇습니다

### 4.4 env 수

`[미확인]` cartpole은 가벼워 24GB에서 문제되지 않을 겁니다. 하지만 **첫 실행은 낮춰서 시작하십시오** — VRAM으로 죽는 건지 설치가 잘못된 건지 구분해야 합니다.

1024 정도로 통과한 뒤 올리십시오. 3.0 CLI에서 이 플래그 이름(`--num_envs`)이 유지되는지는 `--help`로 확인하십시오.

---

## 5. 알려진 함정

### 5.1 의존성 충돌 (Isaac Lab 3.0 beta + Isaac Sim 6.0.0.1) `[문서]`

[IsaacLab #6200](https://github.com/isaac-sim/IsaacLab/issues/6200)에 보고된 `pip check` 충돌입니다.

| 요구하는 쪽 | 충돌 |
| --- | --- |
| `isaaclab` | `coverage==7.6.1` vs `isaacsim-kernel`의 `coverage==7.4.4` |
| `isaaclab-rl` | `packaging<24` vs `isaacsim-core`의 `packaging==26.0` |
| `nvidia-srl-usd` | `numpy<2.0.0` vs `isaacsim-kernel`의 `numpy==2.3.1` |
| `moviepy` | `pillow<12.0` vs `isaacsim-kernel`의 `Pillow==12.1.1` |

이슈는 Done으로 닫혔지만 **해결 내용이 공개돼 있지 않습니다.** 6.0.1 + beta2 조합에서 재현될 수 있습니다.

- `pip check` 경고가 떠도 **학습이 돌면 무시하고 진행하십시오.** 경고를 없애려고 손으로 핀을 맞추다가 환경을 깨는 쪽이 더 위험합니다
- 실제로 import 에러로 죽을 때만 개입합니다. 그때 위 표에서 어느 쌍인지 찾으십시오
- `numpy<2` 충돌은 특히 조심할 것 — numpy 1/2 혼용은 조용히 틀린 값이 아니라 대체로 import 시점에 죽습니다

### 5.2 conda와 uv를 섞지 마십시오

기존 머신은 conda(`env_isaaclab`), 3.0 문서는 uv입니다.
**둘을 같은 셸에서 섞으면 어느 python이 잡히는지 추적이 안 됩니다.** Titan 머신은 uv 한 가지로 가고, conda 환경이 활성화된 셸에서 `uv run`을 부르지 마십시오.

### 5.3 2.x 예제는 그대로 안 됩니다

`[문서]` manager API 제거, Newton 초기화 변경, math 모듈 미사용 커스텀 MDP 깨짐.
블로그·유튜브·포럼 답변은 대부분 2.x 기준입니다. **버전을 먼저 확인하고 붙여넣으십시오.**

### 5.4 헤드리스 wall clock은 속도 지표가 아닙니다

헤드리스 루프는 최대 속도로 돌아 프레임당 계산 비용에 좌우됩니다. 학습 속도를 비교할 때는 **스텝 throughput(FPS)** 으로 재고, 벽시계 시간으로 판단하지 마십시오.
(CES 작업에서 같은 함정으로 1.5배와 3배를 오판한 적이 있습니다. RL에서도 그대로 적용됩니다.)

---

### 5.5 Warp가 한국어 Windows에서 커널 컴파일에 실패합니다 `[실측]`

**이건 우리 코드 문제가 아니라 Warp 버그입니다.** 그리고 조용하지 않고 확실히 죽습니다.

```
File "...\warp\_src\context.py", line 3021, in _compile
    cu_file.write(cu_source)
UnicodeEncodeError: 'cp949' codec can't encode character '—' in position 586886
```

Warp는 생성한 CUDA 소스를 `.cu` 파일로 쓸 때 **인코딩을 지정하지 않습니다.** 그래서 로케일 기본값이 걸리고, 이 머신은 **cp949**입니다. 커널 소스 안에 비 ASCII 문자(여기서는 em dash `—`)가 하나라도 있으면 **컴파일 전에 죽습니다.**

`[실측]` **kamino 솔버 계열 5개가 전부 여기서 죽었습니다** — `kamino_basic_dr_testmech`, `kamino_basic_fourbar`, `kamino_basic_heterogeneous`, `kamino_robot_anymal_d`, `kamino_robot_dr_legs`.

해결은 한 줄입니다. `PYTHONIOENCODING`은 **효과가 없습니다** — 그건 stdio만 덮고, 깨지는 곳은 `open()`입니다.

```
set PYTHONUTF8=1
```

`[실측]` 이걸 주면 `kamino_basic_fourbar`가 0.7초에 끝납니다. **`il.bat`이 이제 자동으로 설정합니다** — 래퍼로 부르면 신경 쓸 것이 없습니다.

**타이탄에서도 같이 터집니다.** 한국어 Windows면 로케일이 같습니다. 래퍼를 안 쓰고 `isaaclab.bat`을 직접 부를 때만 문제가 되니, 그때는 이 변수를 기억하십시오.

이 리포에서 cp949가 문제를 일으킨 **세 번째** 지점입니다 — `.bat` 파일의 한글(래퍼 절), 서브프로세스 stdout, 그리고 이것. 한국어 Windows에서 이 스택을 쓸 때 반복되는 패턴이라고 보는 것이 맞습니다.

---

## 6. cable / cloth — 실제 목표

**결론부터: cloth는 오늘 학습을 걸 수 있고, cable은 예제만 있어서 태스크를 직접 만들어야 합니다** `[실측]`.

| | Newton 예제 | Isaac Lab RL 태스크 |
| --- | --- | --- |
| **cloth** | 8개 | **있음** — `Isaac-Lift-Cloth-Franka-v0` |
| **cable** | 4개 | **없음** — 직접 만들어야 합니다 |

### 6.1 지금 되는 것 — cloth RL

`[실측]` gym 레지스트리(전체 260개)에 등록돼 있는 것을 확인했습니다.

```
Isaac-Lift-Cloth-Franka-v0
Isaac-Lift-Soft-Franka-v0
```

```powershell
.\train.bat --task=Isaac-Lift-Cloth-Franka-v0 --num_envs=16 --max_iterations=10 --headless
```

`franka_cloth_env_cfg.py`를 읽고 확인한 구성 `[실측]`:

| 항목 | 값 |
| --- | --- |
| 솔버 | `CoupledMJWarpVBDSolverCfg` — **MJWarp(강체) + VBD(변형체) 단방향 결합** |
| soft 솔버 | `VBDSolverCfg(integrate_with_external_rigid_solver=True)` |
| cloth 자산 | `MeshRectangleCfg` + `NewtonDeformableBodyPropertiesCfg` |
| 재질 | `NewtonSurfaceDeformableBodyMaterialCfg` |
| 기본 env 수 | **128** (`env_spacing=2.5`) |
| RL config | `FrankaDeformablePPORunnerCfg` (rsl_rl) |

주석에 "matching the Newton example"이라고 적혀 있습니다 — 즉 **6.3의 `cloth_franka` 예제가 이 태스크의 원본**입니다. 예제로 물리를 이해하고 태스크로 학습을 거는 순서가 설계대로입니다.

**8GB에서 cloth 128 env은 아마 안 됩니다** `[미확인]`. cartpole과 달리 변형체는 무겁습니다 — `--num_envs=16`부터 올리십시오.

### 6.2 `contrib` extra는 필요 없습니다 `[실측]`

3절에서 `-i`가 `contrib`를 건너뛴다고 썼는데, **변형체에는 영향이 없습니다.** `isaaclab_contrib`는 core 서브모듈이라 이미 설치돼 있고, MANUAL로 빠진 `contrib` extra는 `rlinf`(다른 RL 프레임워크) 전용입니다.

```
isaaclab_contrib.deformable  ->  import OK
  VBDSolverCfg   CoupledFeatherstoneVBDSolverCfg   CoupledMJWarpVBDSolverCfg
  DeformableObject   DeformableObjectData   NewtonModelCfg
```

**cable 태스크를 직접 만들 때 쓸 API가 이것입니다.** cloth 태스크가 이걸 그대로 쓰고 있으니 복사할 템플릿이 이미 있는 셈입니다.

### 6.3 Newton 예제 — 물리를 먼저 여기서 익히십시오

`[실측]` `newton[examples]`가 설치돼 있어 바로 돌아갑니다. Newton은 **1.2.1**입니다.

**cable (4개)**

| 예제 | |
| --- | --- |
| `cable_twist` | 꼬임 |
| `cable_pile` | 무더기로 쌓기 |
| `cable_bundle_hysteresis` | 번들 이력현상 |
| `cable_y_junction` | Y 분기 |

**cloth (8개)**

| 예제 | |
| --- | --- |
| `cloth_hanging` | **솔버 4개 비교 가능** — `--solver [semi_implicit, style3d, xpbd, vbd]` |
| `cloth_franka` | Franka가 cloth 조작. **6.1 태스크의 원본** |
| `cloth_h1` | 휴머노이드 + cloth 상호작용 |
| `cloth_twist` | 꼬임 |
| `cloth_bending` | 굽힘 |
| `cloth_rollers` | 롤러 통과 |
| `cloth_poker_cards` | 카드 |
| `cloth_style3d` | Style3D 솔버 전용 |

래퍼로 부릅니다.

```powershell
.\il.bat -p -m newton.examples cable_twist
```

헤드리스로 짧게 확인만 할 때:

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver style3d --viewer null --num-frames 30
```

`[실측]` `cable_twist`를 `--viewer null --num-frames 30`으로 **완주했습니다 (exit 0, 에러 0)**.

#### 인자 레퍼런스 — 만들지 않고 조절하는 범위 `[실측]`

> 실행·인자·뷰어를 **작업 중에 찾아보는 형태**로 정리한 것은 [`docs/newton-examples-manual.md`](docs/newton-examples-manual.md)입니다. 이 절은 근거와 함께 남기는 기록이고, 그쪽이 매뉴얼입니다.

런처는 세 가지로 씁니다.

```powershell
.\il.bat -p -m newton.examples              # 인자 없으면 basic_pendulum
```

```powershell
.\il.bat -p -m newton.examples --list       # 전체 68개 목록
```

```powershell
.\il.bat -p -m newton.examples cloth_hanging --help
```

**모든 예제 공통 인자** — `newton/examples/__init__.py`에서 옵니다.

| 인자 | 기본값 | |
| --- | --- | --- |
| `--device DEVICE` | 자동 | Warp 디바이스. `cuda:0`, `cpu` |
| `--viewer {gl,usd,rerun,null,viser}` | **`gl`** | **기본값이 gl이고 이게 "보는" 방법입니다.** `viser`=브라우저, `null`=화면 없음, `usd`=파일 내보내기 |
| `--output-path PATH` | `output.usd` | `--viewer usd`일 때 필수 |
| `--num-frames N` | `100` | 프레임 수 |
| `--headless` / `--no-headless` | off | GL 뷰어에만 해당 |
| `--test` / `--no-test` | off | 테스트 모드 — 종료 상태를 검증합니다 |
| `--quiet` / `--no-quiet` | off | **Warp 컴파일 로그 억제** — 6.5절의 42초 스팸이 사라집니다 |
| `--benchmark [SECONDS]` | off | **워밍업 후 FPS 측정.** 초를 주면 그 시간 또는 `--num-frames` 중 먼저 |
| `--realtime` | off | benchmark 모드에서 프로세스 우선순위 최대 |
| `--warp-config KEY=VALUE` | — | `warp.config` 속성 덮어쓰기. 반복 가능 |
| `--rerun-address` | — | 외부 Rerun 서버 연결 |

**예제 고유 인자는 두 개뿐입니다** `[실측]`. 나머지 예제는 공통 인자만 받습니다.

| 예제 | 고유 인자 |
| --- | --- |
| `cloth_hanging` | `--solver {semi_implicit,style3d,xpbd,vbd}` (기본 **vbd**), `--width 64`, `--height 32` |
| `cable_bundle_hysteresis` | `--segments 40`, `--no-dahl`, `--eps-max 2.0`, `--tau 0.1` |

`cable_bundle_hysteresis`의 인자는 **Dahl 마찰 모델** 파라미터입니다 — `--no-dahl`로 순수 탄성으로 바꾸고, `--eps-max`(최대 소성 변형 [rad])·`--tau`(기억 감쇠 길이 [rad])로 이력 특성을 조절합니다. **cable 쪽에서 파라미터를 만질 수 있는 유일한 예제**라 감을 여기서 잡는 게 이득입니다.

#### 바로 쓰는 조합 `[실측]`

**가장 먼저 이것입니다.** `--viewer`를 생략하면 창이 뜹니다.

```powershell
.\il.bat -p -m newton.examples cloth_hanging
```

창이 안 뜨거나 다른 화면에서 보고 싶으면 브라우저로 갑니다. `viser`·`rerun`·`pyglet`·`OpenGL` 전부 설치돼 있습니다 `[실측]`.

```powershell
.\il.bat -p -m newton.examples cloth_hanging --viewer viser --num-frames 2000 --quiet
```

`[실측]` `viser`가 `http://localhost:8080`에서 listening하는 것을 확인했습니다. 서버는 **예제가 도는 동안만** 살아 있으므로 오래 보려면 `--num-frames`를 크게 주십시오.

아래 셋은 헤드리스·내보내기 쪽으로, 역시 실행해 확인한 것입니다.

되는지만 빠르게 (컴파일 로그 없이):

```powershell
.\il.bat -p -m newton.examples cable_twist --viewer null --num-frames 30 --quiet
```

USD로 내보내 기존 파이프라인에 넣기:

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver style3d --width 32 --height 16 --viewer usd --output-path out\cloth.usd --num-frames 20 --quiet
```

솔버 비교 — 5.4절대로 벽시계가 아니라 FPS로:

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver vbd --benchmark 10 --viewer null
```

`[실측]` `--viewer usd`는 실제로 파일을 씁니다 — `USD output saved in: ...cloth_style3d.usd`, **250 KB**. **이것이 Newton에서 기존 USD 자산 파이프라인으로 나가는 연결점입니다.** GUI 임포터가 없는 kitless에서 특히 값이 있습니다.

`[실측]` Style3D는 `SolverStyle3D::precompute()`에 **2.9초**가 더 듭니다. 솔버를 비교할 때 이 비용을 FPS와 분리해서 보십시오.

**주의 — USD는 내보내기 포맷이고 Newton이 재생해 주지 않습니다.** 생성물은 시간 샘플이 든 애니메이션이 맞습니다 `[실측]` (`0.0→20.0`, 60 FPS, `/root/model/triangles`에 timeSamples 18개). 그런데 **이 머신에는 USD 뷰어가 없습니다** `[실측]` — venv의 `usd-core`에는 `usdview`가 없고, `D:\isaac_601`에도 없습니다. 여는 유일한 길은 `D:\isaac_601\isaac-sim.bat`이고 첫 부팅이 수 분입니다.

**반복 확인에 USD를 쓰지 마십시오.** 보는 것은 `gl`/`viser`, USD는 외부 파이프라인으로 넘길 때만입니다. Newton 안에서 기록·재생하려면 `newton.viewer.ViewerFile("x.bin")` + `replay_viewer` 예제가 맞는 경로입니다.

#### `--warp-config`로 열리는 것 `[실측]`

`warp.config` 속성이 전부 열려 있습니다. 6.5절의 컴파일 비용과 직접 관련된 것만 추립니다.

| 키 | 기본 | 왜 |
| --- | --- | --- |
| `enable_backward` | `True` | **미분이 필요 없으면 `False`로 컴파일이 줄어듭니다.** diffsim 계열이 아니면 해당 |
| `kernel_cache_dir` | `None` | 캐시 위치 변경 — 두 머신에서 분리하거나 공유할 때 |
| `cache_kernels` | `True` | 끄면 매번 재컴파일. 디버깅용 |
| `load_module_max_workers` | `0` | 모듈 로드 병렬화 |
| `ptx_target_arch`, `cuda_arch_suffix` | `None` | **아키텍처 타깃 지정** — Titan sm_75를 파고들 때 |
| `mode` | `'release'` | `'debug'`로 전환 |

```powershell
.\il.bat -p -m newton.examples cable_twist --warp-config enable_backward=False --viewer null --num-frames 30
```

`[미확인]` `enable_backward=False`의 실제 절감폭은 이 머신에서 아직 재보지 않았습니다. 6.5절 표(42.3초)가 기준선입니다.

#### 68개 중 이 프로젝트와 겹치는 것

cable/cloth 외에 D: 드라이브의 기존 자산과 직접 겹치는 것들입니다.

| 예제 | 겹치는 것 |
| --- | --- |
| `contacts_rj45_plug` | **커넥터 삽입** — cable 작업과 바로 이어집니다 |
| `nut_bolt_hydro`, `nut_bolt_sdf` | `bolt_roll`, `bolt_spline` 자산 |
| `basic_conveyor` | 컨베이어 자산 |
| `robot_ur10`, `robot_panda_hydro` | `ur20`, `ur30` 자산 |
| `basic_urdf` | **URDF 로딩** — kitless에 GUI 임포터가 없으므로 여기가 입구입니다 |
| `softbody_franka`, `softbody_dropping_to_cloth` | 변형체-강체 결합 |
| `diffsim_cloth` | 미분 가능 cloth |
| `recording`, `replay_viewer` | 기록·재생 |

### 6.4 솔버 — Newton에 8개 있습니다 `[실측]`

```
SolverVBD   SolverStyle3D   SolverXPBD   SolverMuJoCo
SolverFeatherstone   SolverImplicitMPM   SolverKamino   SolverSemiImplicit
```

- **cloth** → `SolverVBD` 또는 `SolverStyle3D`. Isaac Lab 태스크는 **VBD**를 씁니다
- **cable** → 예제가 `SolverVBD(rigid_avbd_contact_alpha=...)`를 쓰고, 실행하면 **XPBD 커널도 같이 올라옵니다** `[실측]`
- `cloth_hanging` 하나로 4개 솔버를 같은 씬에서 비교할 수 있습니다. **솔버 선택의 근거를 여기서 만드십시오** — 추측으로 고르지 마십시오

### 6.5 Titan 관련 — 커널 컴파일 비용이 여기서 커집니다 `[실측]`

`cable_twist` 첫 실행의 warp 커널 컴파일 내역입니다.

| 모듈 | 시간 |
| --- | --- |
| `xpbd/kernels` | **14.8초** |
| `vbd/rigid_vbd_kernels` (cuda) | **9.0초** |
| `narrow_phase_gjk_mpr` | **8.9초** |
| 그 외 7개 | 9.6초 |
| **합계** | **42.3초** — 10개 컴파일, 3개는 캐시 히트 |

캐시는 `%LOCALAPPDATA%\NVIDIA\warp\Cache\1.13.0`이고, 이 머신은 `sm_89`로 컴파일됐습니다 `[실측]`.

**Titan에서는 `sm_75`로 전부 다시 컴파일됩니다.** 함정 표 2번이 여기서 구체화됩니다 — 그건 실패가 아니라 **첫 실행이 느린 것이 정상**이라는 뜻입니다. cartpole 시작 비용이 66초였고 변형체는 그보다 큽니다. **타이탄 첫 실행이 1~2분 멈춰 보여도 기다리십시오.** 판단 기준은 시간이 아니라 컴파일 **에러 유무**입니다.

### 6.6 cable 태스크를 만드는 순서

없는 것을 만드는 것이니 순서를 지키는 게 이득입니다.

1. `cable_twist`·`cable_y_junction`을 뷰어로 돌려 **거동을 눈으로 확인** — 파라미터 감을 여기서 잡습니다
2. `franka_cloth_env_cfg.py`를 읽고 **cloth 태스크가 Newton 예제를 어떻게 태스크로 감쌌는지** 파악합니다. 이게 유일한 참고 구현입니다
3. `Isaac-Lift-Cloth-Franka-v0`을 낮은 `--num_envs`로 **실제로 학습을 걸어** 변형체 RL이 이 머신에서 도는지 확인합니다 `[미확인]`
4. 그 다음에 cable용 `DeformableObject` + `VBDSolverCfg` 조합으로 태스크를 씁니다

**3번을 2번보다 먼저 하지 마십시오.** 변형체 RL이 8GB에서 도는지 모르는 상태로 새 태스크를 쓰면, 안 될 때 원인이 내 태스크인지 VRAM인지 구분이 안 됩니다.

---

## 7. 그 다음

**전체 실행 경로는 [서베이 7절](docs/rl-operations-survey.md#7-part-e--권고-실행-경로)에 게이트와 함께 정리돼 있습니다.** 아래는 이 문서 범위에서 이어지는 항목입니다.

1. 정책을 GUI에서 재생해 확인 — Titan의 렌더 미달이 실제로 물리는지 여기서 드러납니다
2. 개념 문서 작성 — ManagerBased vs Direct, Observation/Reward/Event/Curriculum Term, 커스텀 로봇 `ArticulationCfg`
3. contact-rich 조립 태스크 (`Isaac-Factory-*`, `Isaac-Forge-*`, `Isaac-AutoMate-*`) — 이 태스크 ID는 로컬 2.3.2 체크아웃에서 확인한 것이므로 `[미확인]` 3.0에서 이름이 유지되는지 확인 필요

---

## 참고 링크

- [`docs/commercial-rl-architectures.md`](docs/commercial-rl-architectures.md) — **상용 RL 아키텍처와 결과물.** 상용 시스템 7개의 관측→정책 구조→행동→학습→보상→안전 계층→결과 수치를 같은 형식으로
- [`docs/commercial-rl-survey.md`](docs/commercial-rl-survey.md) — **상용 RL 서베이.** 지금 실제로 팔리고 돌아가는 RL의 수준. 상용화 등급 T1~T4, 근거를 `[논문]`/`[벤더]`로 분리
- [`docs/rl-operations-survey.md`](docs/rl-operations-survey.md) — **운영 서베이.** 착수 지점 사다리, 평가 프로토콜, 도메인 랜덤화, 회사 요청 목록
- [`docs/ladder-maturity-survey.md`](docs/ladder-maturity-survey.md) — **성숙도 서베이.** 같은 사다리를 도메인 전반(로코모션·이동체·조작·손재주·산업 배치)에서 재조사
- [`docs/how-training-runs.md`](docs/how-training-runs.md) — **학습 실행의 해부.** iteration 한 바퀴의 구조, RL 라이브러리 5종, 모드 A(처음부터) / 모드 B(VLA 후속학습)
- [`docs/newton-examples-manual.md`](docs/newton-examples-manual.md) — Newton 예제 매뉴얼
- [Isaac Lab 설치 문서 (develop)](https://isaac-sim.github.io/IsaacLab/develop/source/setup/installation/index.html) — **명령은 항상 여기와 대조하십시오**
- [kitless 설치 문서 (3.0.0-beta2)](https://isaac-sim.github.io/IsaacLab/release/3.0.0-beta2/source/setup/installation/kitless_installation.html) — **3절 경로 C의 출처**
- [newton-physics/newton](https://github.com/newton-physics/newton) — cable·cloth 예제의 출처. 6절
- [Isaac Lab 3.0 Beta 2 릴리스](https://github.com/isaac-sim/IsaacLab/discussions/6249)
- [Newton Physics Integration](https://isaac-sim.github.io/IsaacLab/main/source/experimental-features/newton-physics-integration/index.html)
- [Isaac Sim 6.0 시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/requirements.html)
- [의존성 충돌 이슈 #6200](https://github.com/isaac-sim/IsaacLab/issues/6200)
- [최소 GPU 문서 불일치 이슈 #311](https://github.com/isaac-sim/IsaacSim/issues/311)

---

## 이 문서를 고치는 방법

`[미확인]` 항목에서 막히거나 통과하면 **그 자리를 `[실측]`으로 바꾸고 실제 값·에러를 적으십시오.**
아래 네 개가 이 문서의 미검증 핵심입니다.

1. `uv run isaaclab train ...` 명령이 실제로 이 형태인지
2. **Newton이 Turing(sm_75)에서 도는지** — 남은 것 중 가장 큰 한 건
3. 6.0.1 GA와 rc 빌드 차이가 실제로 있는지

해소된 것:

- ~~Titan 드라이버가 581.42를 넘는지~~ → 591.86으로 통과 `[실측]` (2026-08-20). 양쪽 머신 동일
