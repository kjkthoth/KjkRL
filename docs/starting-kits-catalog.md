# 기초틀 카탈로그 — 지금 무엇을 받아서 시작하는가

**"맨땅부터는 낡은 방식"의 반대편에 무엇이 있는지를 목록으로 만든 것입니다.**

## 이 조사 전체의 기준선과 비교 축

**기준선** — *"보상만 주고, 무작위 탐색으로 처음부터 수렴시키는 online RL"*.
이 조사는 그것과 오늘의 로봇 RL을 **네 축**에서 비교합니다.

| 축 | 옛날 — 보상만 주고 처음부터 | 오늘 — 무엇을 받고 시작하는가 | 이 조사의 위치 |
| --- | --- | --- | --- |
| **사전 데이터** | 없음. 정책이 스스로 모음 | **ACT는 실물 시연 50개로 시작** · LeRobot 데이터셋 58,000+ · Open X-Embodiment 궤적 100만+, 로봇 22종 | S5 |
| **사전 모델** | 없음. 무작위 초기화 | ACT · Diffusion Policy · **π0(3.5B)** · **GR00T N1.7(3B, 약 6 GB)** · 특권 정보 교사 정책 | S6 · 사다리 L4·L5 |
| **시뮬레이션** | 단일 환경. 실물 또는 느린 시뮬 | **GPU 병렬 4,096 env — 평지 4분 · 험지 20분** · VBD 변형체 · **시스템 식별 + 선택적 랜덤화** | S0 · S1 |
| **미세조정** | 없음. 한 번 학습이 전부 | 교사 → 학생 **증류** · MPC 위 **residual RL** · 사전학습 VLA를 **RL로 후속학습**(RLinf: GRPO·PPO) · **오프라인 RL** | S2 · S7 |

**그런데 기준선 자체가 이미 사전 지식을 받고 있었습니다.**
`[실측]` 우리 cartpole 실행을 [8축](rl-operations-survey.md)에 찍어 보면 **8축 중 6축에서 이미 받고 있습니다** —
관측(완전관측 전체 상태) · 행동 공간(저수준 제어 구조) · 보상(조밀 설계) · 초기 상태 분포(직립 근처) ·
종료 조건(조기 종료) · 환경 자산(검증된 cfg). **맨땅인 축은 정책 초기 가중치와 데이터 둘뿐입니다.**

**그리고 반례** `[문헌]` — **로코모션과 드론에서는 지금도 "보상만 주고 처음부터"가 표준입니다.**
PPO가 다리형 로봇의 de facto 표준이고, 널리 쓰이는 프레임워크가 PPO만 지원하는 경우가 많습니다.
**맨땅이 틀린 것이 아니라 태스크 성질이 정합니다** — 조작은 무작위 정책이 우연히 성공할 확률이 사실상 0이라
보상 신호가 아예 발생하지 않습니다.

앞 문서들이 *"업계가 어떻게 만들었나"*를 다뤘습니다. **이 문서는 *"내가 무엇을 집어 올 수 있나"*입니다.**
이름·출처·무엇을 주는지·우리가 쓸 수 있는지를 계층별로 적었습니다.

> **이 문서가 필요한 이유** — 앞 서베이들이 "맨땅은 사다리의 맨 아래 한 칸"이라고 말해 놓고
> **대안 목록을 제시하지 않았습니다.** 그래서 논지가 반쪽이었습니다.
> **"맨땅"이란 아래 8계층을 전부 직접 만드는 것을 뜻하고, 지금 그렇게 하는 곳은 없습니다.**

## ⚠ 기호 주의 — 사다리 `L#`과 이 문서의 `S#`은 다른 체계입니다

**초판에서 이 문서도 `L#`을 써서 사다리와 충돌했습니다. `S#`(Stack)로 고쳤습니다.**

| 기호 | 무엇을 세는가 | 예 |
| --- | --- | --- |
| **`L0`~`L5`** (사다리) | **착수 지점** — 어디서 시작하는가 | L0 맨땅 · L2 residual · L5 파운데이션 모델 |
| **`S0`~`S8`** (이 문서) | **스택 계층** — 무엇을 받는가 | S0 물리 · S2 RL 라이브러리 · S5 데이터 |

**둘은 대응 관계가 아닙니다.** 예를 들어 사다리 L5(파운데이션 모델 후속학습)를 하려면
스택에서 S6(가중치)·S2(rlinf)·S0(렌더 가능한 시뮬)이 동시에 필요합니다.

## 가용성 표기

**"존재한다"와 "지금 받을 수 있다"는 다릅니다.** 각 항목에 표시했습니다.

| 표기 | 뜻 |
| --- | --- |
| **공개** | 지금 받아서 쓸 수 있음 |
| **게이트** | 받을 수 있으나 접근 승인·계정·라이선스 동의 필요 |
| **미공개** | 논문은 있으나 코드·자산이 아직 안 나옴 |

표기 규칙은 앞 문서들과 같습니다. `[문헌]` 검증 한계도 동일합니다.

---

## 0. 한 장 요약 — 기초틀 8계층

| 계층 | 무엇을 받는가 | 없으면 직접 만들어야 하는 것 |
| --- | --- | --- |
| **S0 물리·시뮬레이터** | 강체·접촉·변형체 솔버, GPU 병렬 | 물리 엔진 |
| **S1 환경 프레임워크** | 관측·보상·종료·커리큘럼 조립 규격 | 환경 API 전체 |
| **S2 RL 라이브러리** | 학습 루프, PPO/SAC/증류 구현 | 알고리즘 구현·분산 학습 |
| **S3 로봇 스타터 킷** | 내 로봇의 URDF·액추에이터·기본 태스크 | 로봇 모델링·튜닝 |
| **S4 태스크·벤치마크** | 태스크 정의와 **평가 지표** | 성공 기준 자체 |
| **S5 데이터** | 시연 궤적·데이터 포맷 | 텔레옵 리그 + 수집 |
| **S6 사전학습 가중치** | 이미 학습된 정책 | 사전학습 전체 |
| **S7 데이터 생성 도구** | 시연 몇 개 → 합성 궤적 다량 | 대량 수집 |
| **S8 평가·운영 도구** | 통계적 비교, 실험 추적 | 평가 방법론 |

**핵심**: 이 8계층은 **전부 기성품이 존재합니다.** 맨땅에서 시작한다는 말은 이걸 전부 새로 만든다는 뜻이고,
그건 2026년에 아무도 하지 않습니다. **간부진 말씀의 구체적 근거가 이 표입니다.**

---

## S0 — 물리·시뮬레이터 `[문헌]`

| 이름 | 무엇을 주는가 | 언제 고르나 |
| --- | --- | --- |
| **Isaac Lab / Isaac Sim** | 수천 env 병렬 + **포토리얼 렌더**. Isaac Gym·OmniIsaacGym을 대체했고 **RL API가 이제 안정** | 인지 기반 태스크, 대규모 env |
| **Newton** | Warp + OpenUSD 기반. **VBD 변형체 솔버(케이블·천·체적)**, MuJoCo Warp·Kamino 강체, SDF 충돌, 하이드로일래스틱 접촉 | **변형체가 목표일 때** |
| **MuJoCo / MJX / MuJoCo Warp** | GPU 병렬 강체. **접촉이 많은 조작에서 물리가 더 정확**하다는 평가 | 파지·손재주·조립 |
| **MuJoCo Playground** | MJX 기반 태스크 모음. **4족·휴머노이드·손·팔 zero-shot sim-to-real** 주장, 단일 GPU 분 단위 학습 | 로코모션 빠른 시작 |
| **mjlab** | Isaac Lab 매니저 API를 MJWarp 위에 올린 경량판. Omniverse 런타임 불필요 | 설치를 가볍게 |
| **Genesis** | 10~80배 빠르다고 보고 | `[미확인]` **아직 주류 기본값 아님** |

**선택 기준이 문헌에 정리돼 있습니다** `[문헌]`:
4족·팔 RL → MuJoCo(MJX) / 포토리얼 인지 + 수천 env → Isaac Lab / **접촉 많은 조작 → MuJoCo 물리가 더 정확**.

> **⚠ 우리 선택과의 긴장** — 위 기준대로면 접촉 많은 조작은 MuJoCo 쪽입니다.
> 그런데 **우리는 변형체(VBD)가 필요해서 Newton/Isaac Lab을 골랐습니다.**
> `[미확인]` **이 상충을 실제 벤치로 확인해야 합니다** — 변형체 요구가 접촉 정확도 요구를 이기는지.

---

## S1 — 환경·태스크 프레임워크

**관측·보상·종료·커리큘럼을 "항(term)"으로 조립하는 규격**을 줍니다. 없으면 환경 API를 직접 설계해야 합니다.

| 이름 | 내용 |
| --- | --- |
| **Isaac Lab 매니저 API** | `ObservationTerm` · `RewardTerm` · `EventTerm` · **`CurriculumTermCfg`** 구성. `CurriculumManager`가 지형 난이도 등을 진행 |
| **Isaac Lab Available Environments** | 등록된 태스크 목록. `[실측]` 우리 체크아웃 gym 레지스트리에 **260개** |
| **mjlab** | 같은 매니저 API를 MJWarp 위에서 |

---

## S2 — RL 라이브러리 `[실측]`

`[실측]` 우리 체크아웃의 통합 학습 진입점이 다섯 개로 분기합니다.

| 이름 | 성격 |
| --- | --- |
| **`rsl_rl`** | **다리형 로코모션 공개 코드가 대부분 이것.** 우리 기본값. **증류 지원 내장** — `RslRlDistillationRunnerCfg`, `rsl_rl_distillation_cfg_entry_point` |
| `rl_games` | Isaac Lab 생태계 통합, iteration별 FPS 통계 |
| `skrl` | 모듈식·확장 지향 |
| `sb3` | 범용 호환성 |
| **`rlinf`** | **VLA 후속학습 전용.** OpenVLA·π0·π0.5·GR00T 지원, GRPO·PPO. `[실측]` **`contrib` extra 필요 — 아직 미설치** |

**라이브러리 선택 근거도 기성품입니다** `[문헌]` — Isaac Lab 문서에 **동일 환경(`Isaac-Humanoid-v0`) · 단일 RTX 4090 ·
65.5M 스텝** 기준 라이브러리별 총 학습 시간 벤치가 있습니다. 추측할 필요가 없습니다.

---

## S3 — 로봇별 스타터 킷 `[문헌]`

**내 로봇의 URDF·액추에이터 모델·기본 태스크가 이미 있는가.**

| 이름 | 내용 |
| --- | --- |
| **legged_gym** | 원조. 험지 로코모션 태스크가 env 파일 + config로 구성. **Isaac Lab으로 마이그레이션됐고 이후 지원은 제한적** |
| **LeggedLab** | legged_gym의 구성 논리를 **Isaac Lab에 이식**해 단순화한 커뮤니티 프로젝트 |
| **`unitree_rl_gym` / Unitree RL Lab** | Go2·H1·H1_2·G1용. 로봇 설정·액추에이터 모델·관측 구성·보상/종료 매니저·명령 샘플링·**커리큘럼·도메인 랜덤화**까지 포함 |
| **Isaac Lab 태스크 템플릿** | `[실측]` `Isaac-Lift-Cloth-Franka-v0` — `CoupledMJWarpVBDSolverCfg` + `NewtonDeformableBodyPropertiesCfg` + `FrankaDeformablePPORunnerCfg` 조합이 **이미 동작하는 상태** |

`[실측]` **우리에게 중요한 것은 마지막 줄입니다** — cloth 태스크 cfg가 **Newton 예제를 Isaac Lab 태스크로 감싼 참조 구현**이고,
주석에 "matching the Newton example"이라고 적혀 있습니다. **cable 태스크는 맨땅이 아니라 이 cfg의 변형입니다.**

---

## S4 — 태스크·벤치마크 스위트 `[문헌]`

**태스크 정의뿐 아니라 "무엇을 성공으로 볼지"를 같이 줍니다.** 이게 없으면 평가 기준을 직접 발명해야 합니다.

| 이름 | 가용성 | 내용 |
| --- | --- | --- |
| **WireCraft** | **미공개** | **산업용 DLO 벤치마크.** 커넥터 삽입 / 클립 라우팅 / 채널 안착 3태스크군, **관절형 + 변형체 두 물리 모델**, 시뮬 + 실물 UR5 궤적, **RL·IL·VLA 공통 지표**. 특권 상태 RL 기준선 **82%+** |
| **DLO-Lab** (ICML 2026) | **공개** | **미분 가능 물리 기반 DLO 조작 벤치마크.** UMass. `[미확인]` 태스크 구성과 우리 목표와의 겹침을 확인해야 함 |
| LIBERO · ManiSkill · RoboTwin · CALVIN | 공개 | `rlinf`가 지원하는 조작 시뮬 스위트 |
| MuJoCo Playground 태스크 | 공개 | 4족·휴머노이드·손·팔 |

> **⚠ 정정 — WireCraft는 지금 받을 수 없습니다.** `[문헌]` 논문이 **"게재 확정 시 공개 예정"**이라고 밝히고 있고,
> 공개 범위는 시뮬 벤치마크·궤적 데이터·데이터 생성 도구·**3D 프린트 태스크보드 부품**까지입니다.
> 초판 카탈로그가 이것을 "집어 올 수 있는 것"으로 분류했는데 **오류였습니다.**
>
> **게다가 기반이 Isaac Lab 2.2.1 / Isaac Sim 4.5입니다** — `[실측]` 우리는 3.0.0-beta2 + Newton이라
> 공개되더라도 코드를 그대로 쓸 수 없습니다. **지금 가져올 수 있는 것은 논문에 적힌 태스크 분류와 평가 지표뿐입니다.**
>
> `[자작]` **대안 판단** — S4를 당장 채우려면 **DLO-Lab을 먼저 보고**, WireCraft는 공개를 기다리며
> **지표 체계만 차용**하는 것이 맞습니다.

---

## S5 — 데이터 `[문헌]`

| 이름 | 규모·내용 |
| --- | --- |
| **LeRobot Hub** | **2026-05 기준 데이터셋 58,000개 이상.** 2024년 말 1,145개에서 증가, Hugging Face Hub **최대 카테고리**. `LeRobotDataset` 포맷 |
| **Open X-Embodiment** | **실물 로봇 궤적 100만+ , 로봇 형태 22종.** 34개 연구실의 **60개 데이터셋을 통합**, RLDS 에피소드 포맷. 21개 기관 참여 |

**한계도 명확합니다** `[문헌]` — LeRobot 기여가 **팔 조작에 편중**돼 있고 로코모션·내비게이션은 과소 대표입니다.
포맷 표준화가 진행 중이고, 그것이 **이종 하드웨어 범용 파운데이션 모델의 선행 조건**입니다.

`[미확인]` **변형체 조작 궤적이 이 안에 얼마나 있는지는 확인이 필요합니다.** 있으면 L5를 받고 시작할 수 있고,
없으면 우리 태스크에서 L5는 비어 있는 칸입니다.

---

## S6 — 사전학습 가중치 `[문헌]`

**정책을 처음부터 학습하지 않고 받아서 시작하는 층입니다.** LeRobot이 순수 PyTorch로 통합해 두었습니다.

**모방학습 계열**

| 이름 | 특징 |
| --- | --- |
| **ACT** (Action Chunking with Transformers) | 조건부 VAE + 트랜스포머로 **행동 청크를 한 번의 전방 계산으로 예측**. **업로드 수 1위** — 작고 추론이 빠르며 **실물 시연 50개 정도로도 쓸 만한 정책**이 나오는 것이 이유 |
| **Diffusion Policy** | 행동 궤적을 조건부 디노이징 확산으로 모델링. CNN 시각 인코더 |
| VQ-BeT · Multitask DiT | |

**VLA 계열**

| 이름 | 규모·특징 |
| --- | --- |
| **π0** | **약 35억 파라미터**, flow-matching. 다양한 멀티로봇 조작 데이터로 사전학습 |
| π0-Fast · **π0.5** | 개방 세계 일반화 |
| **GR00T N1.7** | **3B 파라미터, `nvidia/GR00T-N1.7-3B`.** 첫 실행 시 HF에서 자동 다운로드(**약 6 GB**), **NVIDIA Open Model License — 상업적 이용 가능**. LIBERO·DROID 파인튜닝판도 별도 공개, **LeRobot에 통합**. `[문헌]` **⚠ VLM 백본 `nvidia/Cosmos-Reason2-2B`가 gated model이라 별도 접근 요청 필요 — 즉 "게이트"입니다** |
| **SmolVLA** | **약 4.5억 파라미터 경량.** LeRobot **커뮤니티 데이터로 학습**, 언어 조건 실물 제어 |
| XVLA · EO-1 · MolmoAct2 · WALL-OSS · EVO1 | |

**"ACT + 시연 50개"가 이 문서에서 가장 실무적인 숫자입니다** — S3(시연 기반)의 진입 비용이 그 정도입니다.

---

## S7 — 데이터 생성·증강 도구 `[문서]`

**시연을 적게 모으고 늘리는 층입니다.**

| 이름 | 내용 |
| --- | --- |
| **Isaac Lab Mimic** | MimicGen 계열. 사람 시연을 **객체 중심 서브태스크로 분절 → 강체 변환 → 재조합**. **시연 1개에서도** 사실상 무한한 합성 궤적, 병렬 env로 생성 처리량 확대 |
| **SkillGen** | Mimic + 모션 플래닝. 충돌 없는 적응형 궤적 |
| RoboGen · GenSim2 | 생성형 태스크·환경 자동 생성. **단 생성 데이터가 실물로 전이되지 않는다는 것이 문헌 평가** |

`[문서]` **요청 1(Isaac Sim 설치) 승인으로 Mimic·SkillGen이 열렸습니다.** kitless에서는 빠져 있던 층입니다.

---

## S8 — 평가·운영 도구 `[논문]`

| 이름 | 내용 |
| --- | --- |
| **rliable** | 계층 부트스트랩 신뢰구간, **IQM(사분위 평균)**, 성능 프로파일. **태스크당 5회 실행 점추정 비교의 제1종 오류가 50%를 넘는다**는 결과에 대한 대응 |
| 실험 추적 | `[실측]` rsl_rl이 실행마다 `params/agent.yaml`, `params/env.yaml`, `git/IsaacLab.diff`를 남깁니다 — 계보의 절반은 이미 있음 |

---

## 9. 우리가 이미 받은 것 / 아직 안 받은 것 `[실측]`

**8계층을 우리 프로젝트에 대고 채점하면 이렇습니다.**

> **⚠ 이 표를 "업계는 S2까지만 상용화했다"로 읽으면 정반대입니다.**
> **"업계 가용성" 열이 업계 상태이고, "우리" 열은 우리가 받아 놓았는지입니다.**
> **S3~S8도 전부 이미 존재하며 대부분 지금 무료로 받을 수 있습니다** — 우리가 아직 안 받았을 뿐입니다.

| 계층 | 업계 가용성 | 우리 | 내용 |
| --- | --- | --- | --- |
| S0 물리 | 공개 | **받음** | Newton 1.2.1 — VBD 변형체가 선택 이유 |
| S1 환경 | 공개 | **받음** | Isaac Lab 3.0.0-beta2 매니저 API |
| S2 RL 라이브러리 | 공개 | **받음** | `rsl_rl` (+`rlinf`는 `contrib` extra 미설치) |
| S3 로봇 스타터 | 공개 | **절반** | cloth 태스크 cfg는 있음 / **cable은 없음 — 직접 만들어야 함** |
| S4 벤치마크 | **WireCraft 미공개** / DLO-Lab 공개 | **절반** | WireCraft는 공개 대기 + 버전 불일치 → **지표만 차용**. DLO-Lab 확인 필요 |
| S5 데이터 | 공개 (LeRobot·OXE) | **없음** | 변형체 시연 없음. `[미확인]` 공개 데이터에 있는지 확인 필요 |
| S6 사전학습 가중치 | **게이트** (Cosmos 백본 승인) | **없음** | 승인으로 **가능해졌으나 아직 안 씀** |
| S7 데이터 생성 | 공개 | **열림** | 요청 1 승인으로 Mimic·SkillGen 사용 가능. **아직 안 씀** |
| S8 평가 도구 | 공개 | **없음** | rliable 미도입. 판정 기준 미정 |

**받은 것 3 / 절반 2 / 안 받은 것 4.**
**그런데 업계 가용성 열을 보면 미공개는 WireCraft 하나뿐이고, 게이트가 하나(GR00T 백본), 나머지 전부 공개입니다.**
**즉 빈 칸은 "업계에 없어서"가 아니라 "우리가 아직 안 받아서"입니다.**

**여기서 나오는 실행 순서** `[자작]`:

1. **L4를 먼저 채우십시오** — WireCraft의 태스크 분류와 지표를 우리 평가 기준으로 확정. **비용 0, 나머지 전부의 전제**
2. **L8을 그 다음에** — 5시드·IQM·부트스트랩 CI 규칙. 나중에 정하면 쌓인 실험을 버립니다
3. **L3은 cloth cfg 변형으로** — 맨땅 아님
4. **S5·S6·L7은 태스크 모드가 정해진 뒤에** — 상태 기반이면 필요 없고, 카메라·언어 기반이면 전부 필요

---

## 10. 미확인

| # | 확인할 것 |
| --- | --- |
| 1 | **S0 상충** — 접촉 많은 조작은 MuJoCo 물리가 더 정확하다는 평가 vs 우리는 변형체 때문에 Newton. 실제 벤치로 확인 |
| 2 | **공개 데이터에 변형체 조작 궤적이 있는지** — LeRobot Hub·Open X-Embodiment 검색 |
| 3 | Isaac Lab 3.0-beta2에 `RslRlDistillationRunnerCfg` 계열이 실제로 있는지 |
| 4 | `contrib` extra 설치 명령과 의존성 충돌 여부 |
| 5 | Isaac Lab 라이브러리 비교 벤치 표의 실제 수치 |
| 6 | ACT가 **변형체 태스크에서도 "시연 50개"** 수준으로 성립하는지 — 강체 조작 기준 수치임 |
| 7 | **DLO-Lab의 태스크 구성**과 우리 목표(케이블 라우팅·커넥터 삽입)의 겹침 — S4를 당장 채울 수 있는 유일한 후보 |
| 8 | **WireCraft 공개 시점** — 게재 확정 시 공개 예정 |
| 9 | `nvidia/Cosmos-Reason2-2B` **접근 요청 절차와 소요 시간** — S6 진입의 실제 관문 |

---

## 11. 참고 문헌

**시뮬레이터**
- [Choosing a robotics simulator in 2026 (RobotForge)](https://robotforge.org/tutorials/simulators/choosing-a-simulator-2026) — **선택 기준의 출처**
- [MuJoCo Playground](https://playground.mujoco.org/) · [mjlab (arXiv 2601.22074)](https://arxiv.org/abs/2601.22074)
- [newton-physics/newton](https://github.com/newton-physics/newton) · [Isaac Lab 논문 (arXiv 2511.04831)](https://arxiv.org/abs/2511.04831)

**프레임워크·스타터 킷**
- [Isaac Lab — Available Environments](https://isaac-sim.github.io/IsaacLab/main/source/overview/environments.html)
- [Isaac Lab — Curriculum Utilities](https://isaac-sim.github.io/IsaacLab/main/source/how-to/curriculums.html)
- [leggedrobotics/legged_gym](https://github.com/leggedrobotics/legged_gym) · [LeggedLab](https://github.com/Hellod035/LeggedLab)
- [unitreerobotics/unitree_rl_gym](https://github.com/unitreerobotics/unitree_rl_gym)
- [RL 라이브러리 비교 (Isaac Lab 문서)](https://isaac-sim.github.io/IsaacLab/main/source/overview/reinforcement-learning/rl_frameworks.html)

**벤치마크**
- [WireCraft (arXiv 2606.18097)](https://arxiv.org/abs/2606.18097) — 우리 태스크에 가장 가까우나 **코드 미공개(공개 예정)**
- [DLO-Lab (ICML 2026, UMass)](https://github.com/UMass-Embodied-AGI/DLO-Lab) — **미분 가능 물리 DLO 벤치마크. 공개돼 있음**

**데이터**
- [LeRobot (arXiv 2602.22818)](https://arxiv.org/abs/2602.22818) · [huggingface/lerobot](https://github.com/huggingface/lerobot)
- [Open X-Embodiment (arXiv 2310.08864)](https://arxiv.org/abs/2310.08864) · [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment)

**사전학습 가중치**
- [SmolVLA (Hugging Face)](https://huggingface.co/blog/smolvla)
- [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) · [nvidia/GR00T-N1.7-3B (가중치)](https://huggingface.co/nvidia/GR00T-N1.7-3B) · [GR00T 1.7 in LeRobot](https://huggingface.co/blog/nvidia/nvidia-isaac-teleop-and-gr00t17-in-lerobot)
- [Isaac Lab — RL Post-Training for VLA Models](https://isaac-sim.github.io/IsaacLab/develop/source/experimental-features/rlinf_vla_posttraining.html)

**데이터 생성·평가**
- [Isaac Lab Mimic](https://isaac-sim.github.io/IsaacLab/main/source/overview/imitation-learning/teleop_imitation.html) · [SkillGen](https://isaac-sim.github.io/IsaacLab/main/source/overview/imitation-learning/skillgen.html)
- [Deep RL at the Edge of the Statistical Precipice (NeurIPS 2021)](https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf) · [rliable](https://research.google/blog/rliable-towards-reliable-evaluation-reporting-in-reinforcement-learning/)
