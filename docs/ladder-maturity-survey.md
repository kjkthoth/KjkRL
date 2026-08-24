# 칸별 성숙도 서베이 — 도메인 전반에서 L0~L5가 어디까지 왔는가

**이 문서는 `rl-operations-survey.md`의 사다리를 프로젝트 체크리스트가 아니라 조사 축으로 다시 쓴 것입니다.**

앞 문서는 각 칸을 **"우리 kitless 스택에서 되는가"**로만 판정했습니다. 그건 지시의 절반만 답한 것입니다.
간부진 지시는 **"전반적으로 어떻게 운영하는지"** 였으므로, 같은 칸을 **도메인 전반에서 얼마나 성숙했는가**로 다시 봅니다.
cable/cloth 한정을 걷어냈습니다.

| 문서 | 축 |
| --- | --- |
| `rl-operations-survey.md` | 우리 스택 가용성 + 운영 규율 + 회사 요청 |
| **이 문서** | **도메인 전반 성숙도.** 로코모션·이동체·조작·손재주·산업 배치 |

## 표기 규칙

앞 문서와 같습니다 — `[실측]` `[문서]` `[문헌]` `[자작]` `[미확인]`.

> **`[문헌]` 검증 한계는 앞 문서와 동일합니다.** arxiv·공식 문서 직접 열람이 egress 정책으로 차단된 환경에서
> 작성됐고, 모든 `[문헌]`은 **검색 요약 기반이며 1차 원문 대조를 하지 않았습니다.**
> 이 문서는 앞 문서보다 `[문헌]` 비중이 훨씬 높습니다. **수치를 외부에 인용하기 전에 원문을 대조하십시오.**

### 성숙도 등급 `[자작]`

**이 5단계는 제가 정한 것입니다.** 업계 표준 척도가 아닙니다.

| 등급 | 뜻 |
| --- | --- |
| **상용** | 여러 팀이 재현 절차로 일상 사용. 라이브러리 기본값에 들어가 있음 |
| **정착** | 다수 논문·오픈소스 레시피 존재. 해당 도메인의 표준 접근 |
| **확산 중** | 일부 도메인에서 검증됨. 다른 도메인으로 이식이 진행 중 |
| **연구** | 결과가 팀·태스크에 강하게 의존. 핵심 난점이 미해결 |
| **제한적** | 원리상 가능하지만 그 도메인에서는 잘 안 쓰임 |

---

## 0. 이 서베이의 결론 — 프레임이 하나 깨졌습니다

**세 줄 요약**

1. **사다리가 아니라 고리입니다.** L5(파운데이션 모델)의 2026년 프론티어가 **RL 후속학습**입니다 — πRL, VLA-RFT, RLinf-VLA, CO-RFT, Probe-Learn-Distill. 즉 **맨 위 칸이 맨 아래 칸의 기법으로 되돌아옵니다.** "위로 올라가면 끝"이라는 제 원래 그림은 틀렸습니다 `[자작]` 정정
2. **무게 중심은 L4입니다.** 특권 정보 교사-학생 증류가 로코모션·휴머노이드 로코조작·손재주·비전 조작에서 **전부 표준**입니다. 사다리에서 가장 널리 퍼진 칸이 맨 위가 아니라 위에서 두 번째입니다 `[문헌]`
3. **L0은 죽지 않았습니다.** 로코모션과 드론에서 **맨땅 + 대규모 병렬 PPO가 여전히 de facto 표준**입니다 `[문헌]`. "맨땅은 안 쓴다"가 아니라 **"도메인에 따라 맨땅이 정답이다"**가 정확한 서술입니다 — 앞 문서의 톤을 여기서 교정합니다

**즉 간부진 말씀은 여전히 맞지만, 이유가 제가 앞 문서에 쓴 것과 다릅니다.**
"업계는 맨땅에서 시작하지 않는다"가 아니라 **"업계는 도메인별로 어느 칸에서 시작할지 판단한다"**입니다.
우리 태스크(접촉 많은 조작)에서 맨땅이 나쁜 선택인 것은 사실이지만, 그건 **업계 관행이 아니라 태스크 성질**에서 나옵니다.

---

## 1. 성숙도 매트릭스

**행이 칸, 열이 도메인입니다.** 한 칸의 성숙도는 도메인마다 다릅니다 — 이게 이 서베이의 핵심 관찰입니다.

| 칸 | 로코모션 (4족·휴머노이드) | 이동체 (드론·내비) | 조작 (pick-place·조립) | 손재주 (in-hand·그리핑) | 산업 현장 배치 |
| --- | --- | --- | --- | --- | --- |
| **L0** 맨땅 | **상용** | **상용** | 제한적 | 제한적 | 제한적 |
| **L1a** 검증 자산·프레임워크 재사용 | **상용** | **상용** | **상용** | **정착** | 정착 |
| **L1b** 생성형 태스크·환경 자동 생성 | 연구 | 연구 | **연구** | 연구 | — |
| **L2** 프리미티브 + Residual | **정착** ↑ | 정착 | **정착** | 확산 중 | 정착 |
| **L3** 시연 기반 (IL) | 확산 중 | 제한적 | **상용** ↑ | **정착** | **정착** ↑ |
| **L4** 특권 정보 교사-학생 | **상용** | 정착 | **정착** | **정착** ↑ | 확산 중 |
| **L5** 파운데이션 모델 | 확산 중 | 연구 | **확산 중** ↑↑ | 확산 중 | 확산 중 |
| **신흥** 학습된 시뮬·월드 모델 | 연구 | **확산 중** | 연구 | 연구 | — |

`↑` = 2025–2026에 등급이 올라간 것, `↑↑` = 가장 빠르게 움직이는 칸.

**매트릭스에서 읽어야 할 것 세 가지.**

- **L0의 분포가 극단적입니다** — 로코모션·드론에서 상용, 조작·손재주에서 제한적. **같은 기법이 도메인에 따라 정반대 등급입니다**
- **L4가 가장 고르게 높습니다** — 어느 열에도 "연구"가 없습니다. 이게 무게 중심입니다
- **L1b만 전 도메인에서 연구 등급입니다** — 규모는 나오는데 전이가 안 됩니다 (3.2절)

---

## 2. L0 — 맨땅: 로코모션에서는 여전히 표준입니다

### 2.1 상태 `[문헌]`

**PPO가 다리형 로봇의 de facto 표준입니다.** 대규모 병렬 시뮬(Isaac Lab 등)에서의 견고성·확장성 때문이고,
널리 쓰이는 학습 프레임워크가 **PPO만 지원하는 경우가 많습니다** — 온폴리시 RL을 병렬 env로 올리기 쉬워서입니다.
2025–2026 연구에서도 기초 로코모션 정책을 **정규화 페널티 하에 맨땅에서 학습**하는 방식이 유지됩니다.

**드론은 더 강합니다.** 궤적 추종 zero-shot sim-to-real은 사실상 정리된 문제입니다.
`[문헌]` SimpleFlight 계열 연구가 zero-shot 배포를 위한 **5개 요소**를 특정했습니다.

| # | 요소 |
| --- | --- |
| 1 | actor 입력에 **속도와 회전행렬** 포함 |
| 2 | critic 입력에 **시간 벡터** 포함 |
| 3 | **행동 차분 정규화** (부드러움) |
| 4 | **시스템 식별 + 선택적 랜덤화** |
| 5 | 학습 시 **큰 배치 크기** |

Crazyflie 실물에서 벤치마크 궤적 전부를 완주한 유일한 정책이었고, SOTA RL 기준선 대비 추종 오차를 **50% 이상** 줄였습니다.

**4번 항목을 기억하십시오.** 앞 문서 6.3·6.4절(도메인 랜덤화 + 시스템 식별)이 **전혀 다른 도메인에서 독립적으로 같은 결론**에 도달한 것입니다.

### 2.2 알고리즘 — 오프폴리시 전환은 아직 표준 조언이 아닙니다

**앞 문서의 톤을 교정합니다.** 앞 문서 4.5절에서 "표본 효율이 문제면 알고리즘 교체가 실재하는 선택지"라고 썼는데,
문헌 상태는 그보다 미묘합니다.

`[문헌]` **SAC는 대규모 병렬 환경에서 PPO의 경험적 성능을 일관되게 따라잡지 못했습니다.**
2026년에 그 격차를 메우는 작업이 진행 중입니다 — RSL-RL-SAC(`Bridging the Gap: Enabling Soft Actor Critic for
High Performance Legged Locomotion`)이 그 자체로 "격차가 있었다"는 증거입니다.
FastTD3/FastSAC의 15분 사례는 **오프폴리시가 되는 조건을 찾은 결과**이지, 오프폴리시가 기본값이 됐다는 뜻이 아닙니다.

**실무 결론:** PPO로 시작하십시오. 표본 효율이 실제로 병목이라고 **측정된 뒤에** 오프폴리시를 검토하십시오.

### 2.3 왜 조작에서는 제한적인가

앞 문서 2절에 쓴 그대로입니다 — 보상 신호가 발생하지 않습니다. 다만 이제 도메인 대비로 말할 수 있습니다.
**로코모션은 무작위 몸부림에서도 전진 보상이 나오고, 드론은 상태가 저차원이고 목표가 궤적으로 주어집니다.
조작은 둘 다 아닙니다.** 그래서 조작 열에서만 L0가 내려갑니다.

---

## 3. L1 — 두 갈래로 쪼개야 합니다

앞 문서에서 L1을 "문헌 용어가 없는 가장 약한 칸"으로 적었습니다. **절반만 맞았습니다.**
갈래를 나누면 한쪽은 상용이고 한쪽은 실재하는 연구 영역입니다.

### 3.1 L1a 검증 자산·프레임워크 재사용 — 상용 `[문헌]`

문헌 용어는 여전히 없습니다. **엔지니어링 관행이지만 인프라는 성숙했습니다.**

| 층 | 현황 |
| --- | --- |
| 시뮬·환경 프레임워크 | Isaac Lab, MuJoCo Playground, mjlab, Isaac Sim |
| RL 라이브러리 | rsl_rl(RSL-RL 라이브러리 논문 별도 존재), rl_games, skrl |
| **데이터 커먼즈** | **LeRobot Hub — 2026-05 기준 데이터셋 58,000개 이상.** 2024년 말 1,145개에서 증가, Hugging Face Hub 최대 카테고리 |
| 자산 표준 | OpenUSD, SimReady (Lightwheel 등이 정의 참여) |

`[문헌]` LeRobot은 하드웨어 인터페이스·데이터 수집·스트리밍·학습·추론을 한 스택으로 묶는 오픈소스 라이브러리이고,
2026년은 **오픈소스 로봇 학습 스택이 production-grade가 된 시점**으로 평가됩니다.

**한계도 명확합니다** `[문헌]` — 커뮤니티 기여가 **팔 조작에 편중**돼 있고 로코모션·내비게이션은 과소 대표입니다.
포맷 표준화가 아직 진행 중이고, 이게 **이종 하드웨어 범용 파운데이션 모델의 선행 조건**입니다.

### 3.2 L1b 생성형 태스크·환경 자동 생성 — 연구 `[문헌]`

**이건 실재하는 연구 영역입니다.** 앞 문서에서 놓쳤습니다.

| 시스템 | 무엇을 하는가 |
| --- | --- |
| **RoboGen** (ICML) | 생성 모델로 **태스크 제안 → 씬 생성 → 학습 감독 생성 → 스킬 학습** 4단계 자동화 |
| **GenSim2** | 코딩 LLM으로 시뮬 태스크 생성. **관절 태스크 100종 × 객체 200개**까지 데이터 생성 |
| GenDexHand | 손재주용 생성형 시뮬 |
| V-Dreamer | 영상 생성 사전지식으로 시뮬·궤적 합성 |

**그리고 이 갈래의 핵심 한계가 문헌에 명시돼 있습니다** `[문헌]` —
**RoboGen류는 조작 태스크에 RL을 쓰지만 생성된 데이터가 비현실적이고 실물로 전이되지 않습니다.**
GenSim은 상대적으로 단순한 top-down pick-place에 머물러 있습니다.

**즉 규모는 해결됐고 전이가 미해결입니다.** L1b를 "무한 데이터"로 읽으면 안 됩니다.
**지금 값이 있는 곳은 시뮬 내 사전학습·커리큘럼 생성이고, 실물 이전 데이터로는 아직 아닙니다** `[미확인]`.

---

## 4. L2 — 2026에 등급이 올라간 칸

**앞 문서는 L2를 2018년 Siemens residual RL로 소개했습니다. 지금은 그 그림이 낡았습니다.**

`[문헌]` **Residual MPC** (2025-10) 가 이 칸을 GPU 시대로 옮겼습니다.

| 구성 | 내용 |
| --- | --- |
| 구조 | MPC와 RL을 **토크 제어 수준에서 블렌딩**하는 GPU 병렬 잔차 아키텍처 |
| MPC | **kinodynamic 전신 MPC를 수천 에이전트에 대해 100 Hz로 병렬 평가** |
| 구현 | KKT 행렬 분해에 NVIDIA cuDSS, 보조 함수는 CusADi 코드 생성 |
| 역할 | 모델 기반 사전지식이 **강한 편향으로 작동해 단순한 보상 집합만으로 정책을 유도** |
| 결과 | 단독 MPC·엔드투엔드 RL 대비 **표본 효율↑, 점근 보상↑, 추종 가능 속도 명령 범위 확장, 미지 걸음새·불균일 지형 zero-shot 적응** |

관련 축으로 **MPC-Guided RL for Scalable Humanoid Control**이 있습니다.

**이게 왜 중요한가.** L2는 "RL이 약할 때 쓰는 우회로"가 아닙니다.
**모델 기반 제어를 사전지식으로 넣으면 보상 설계 부담이 줄어든다**는 것이 이 칸의 값이고,
앞 문서 6.5절(보상 거버넌스)과 직접 연결됩니다 — **보상 항이 적으면 해킹 표면도 작습니다.**

---

## 5. L3 — 데이터 스케일링 법칙이 나왔습니다

### 5.1 시연 수보다 다양성이 지배합니다 `[문헌]`

**이 서베이에서 가장 실무적으로 값이 큰 발견입니다.**
시연 40,000개 수집 + 실물 rollout 15,000회 이상으로 수행된 연구 결과입니다.

| 발견 | 내용 |
| --- | --- |
| 스케일링 형태 | 일반화 성능이 **환경 수·객체 수에 대해 대략 거듭제곱 관계** |
| **지배 요인** | **환경·객체 다양성이 시연 절대 수보다 훨씬 중요합니다.** 환경/객체당 시연 수가 일정 임계를 넘으면 추가 시연은 효과가 거의 없습니다 |
| 권고 배치 | **환경 32개 × 각 1개 고유 객체 × 시연 50개** |
| 실측 비용 | **수집 인원 4명 × 반나절** → 신규 환경·미지 객체에서 두 태스크 약 **90% 성공** |

**운영 함의가 큽니다.** "시연을 많이 모으자"는 방향이 틀렸습니다.
**같은 셋업에서 1,000개를 모으는 것보다 32개 셋업에서 50개씩 모으는 것이 낫습니다.**
회사에 요청할 것도 "텔레옵 인력"이 아니라 **"서로 다른 환경·객체 구성"**입니다.

### 5.2 극단으로 가면 시연 1개 `[문헌]`

`Crossing the Human-Robot Embodiment Gap with Sim-to-Real RL using One Human Demonstration` —
**인간 시연 1개**로 sim-to-real RL을 성립시킨 사례입니다. L3와 L0의 경계가 흐려지는 지점입니다.

합성 증강 쪽은 앞 문서와 동일합니다 — Isaac Lab Mimic(MimicGen 계열), SkillGen.

---

## 6. L4 — 무게 중심. 도메인 전반 표준입니다

**매트릭스에서 어느 열에도 "연구"가 없는 유일한 칸입니다.**

### 6.1 도메인별 형태 `[문헌]`

| 도메인 | 구현 | 특징 |
| --- | --- | --- |
| 로코모션 | 특권 상태 교사 → 노이즈 관측 학생 | 2022년 이후 주류 |
| **휴머노이드 로코조작** | **VIRAL** — 특권 RL 교사(전체 상태)가 장기 로코조작 학습 → **비전 학생**을 tiled rendering 대규모 시뮬에서 **online DAgger + BC 혼합**으로 증류 | **컴퓨트 규모가 결정적: 시뮬을 수십 GPU(최대 64)로 확장해야 교사·학생 학습이 안정** |
| **손재주 (촉각)** | **PTLD** — 특권 센서 정책을 시뮬 RL로 학습 → 실물 계측 셀에서 촉각 시연 수집 → **촉각 인코더가 특권 인코더의 잠재를 모방.** 촉각 시뮬을 아예 우회 | in-hand rotation 벤치마크에서 **+182%** |
| 손재주 (관절 도구) | 특권 oracle → 자기수용감각 학생. 실물 촉각·모터 토크로 cross-attention 접촉 적응 | |
| 비전 조작 (휴머노이드) | **자동 real-to-sim 튜닝** + 접촉 상태/객체 상태로 **분리된 보상** + task-aware 손 자세 + **divide-and-conquer 증류** | 3개 태스크 실물 성공 |

**PTLD의 트릭을 눈여겨보십시오** — 시뮬하기 어려운 감각(촉각)을 **시뮬하지 않고**, 실물 데이터를 특권 잠재 공간으로
인코딩합니다. 변형체·접촉처럼 시뮬 충실도가 의심스러운 곳에 일반적으로 적용 가능한 패턴입니다 `[미확인]`.

### 6.2 L4의 한계 — 정직하게 `[문헌]`

**2단계 교사-학생은 공짜가 아닙니다.**

- **데이터 효율이 낮습니다**
- **학생이 교사보다 성능이 떨어지는 일이 흔합니다**

**더 싼 대안이 있습니다 — asymmetric actor-critic.** critic에만 전체 상태를 주고 actor는 부분 관측만 받습니다.
시뮬 내 정책 학습을 **단일 단계로 단순화**합니다 — 특권 잠재 증류의 2단계를 1단계로 줄이는 것입니다.

**실무 순서 권고** `[자작]`: **asymmetric actor-critic을 먼저 시도하고, 부족할 때 2단계 증류로 가십시오.**
앞 문서 7절 실행 경로의 7·11번(교사 → 학생)은 이 선택지를 고려하지 않았습니다.

### 6.3 운영 함의 — 컴퓨트가 레시피의 일부입니다

**VIRAL의 "최대 64 GPU"를 그냥 넘기지 마십시오.** 비전 학생까지 가는 L4는 **단일 GPU 작업이 아닙니다.**
앞 문서 8절 요청 2번(GPU 1장)은 **교사 단계까지의 요청**으로 범위를 명확히 해야 하고,
비전 학생이 목표가 되는 순간 요청 규모가 달라집니다 `[미확인]` — 우리 태스크에서 필요한 실제 규모는 측정 대상입니다.

---

## 7. L5 — 가장 빠르게 움직이고, 고리를 만듭니다

### 7.1 현재 지형 `[문헌]`

| 계열 | 모델 | 특징 |
| --- | --- | --- |
| Physical Intelligence | π0 → **π0.5** → **π0.7** | π0.5는 개방 세계 일반화, diffusion flow로 행동 생성. π0.7은 **steerable generalist + 창발 능력** 보고 |
| NVIDIA | GR00T N1 → N1.5 → **N1.7** | **인간 1인칭 영상 20,000시간 이상(EgoScale) + Isaac 합성 데이터** |
| Google | **Gemini Robotics 1.5** | **Motion Transfer**로 이종 로봇 플랫폼 데이터를 단일 표현 공간으로 통합 |
| 오픈 | OpenVLA (7B, LLaMA-2 백본) | |

`[문헌]` 세 선두 아키텍처의 철학이 갈립니다 — **NVIDIA는 뇌를 둘로 분리, Google은 행동 전에 사고, PI는 diffusion flow.**

**앞 문서를 갱신합니다** — 앞 문서는 GR00T N1.5를 최신으로 적었는데 **N1.7이 있습니다.**

### 7.2 그리고 고리 — L5가 RL로 되돌아옵니다 `[문헌]`

**이게 이 서베이의 구조적 발견입니다.**

`[문헌]` **RL 후속학습이 시연 기반 초기화를 넘어 VLA 정책을 개선하는 유망한 접근으로 부상**했습니다.
행동 복제·지도 미세조정과 달리 온라인 RL은 **정책이 자기 상호작용 데이터를 모아 태스크 수준 성공 신호를 직접 최적화**합니다.

| 계열 | 접근 |
| --- | --- |
| πRL, ReinFlow, VLA-R1 | SFT 후 온라인 RL, flow 기반 정책 미세조정, 추론 지향 후속학습 |
| **VLA-RFT** | **월드 시뮬레이터 안에서 검증된 보상**으로 강화 미세조정 |
| RLinf-VLA | VLA용 RL 통합·효율 프레임워크 |
| CO-RFT | 청크 오프라인 RL 미세조정 |
| EXPO-FT, Z-1 | 표본 효율 개선 |
| **Probe · Learn · Distill** | **residual RL + 분포 인식 데이터 수집**의 3단계. 비싼 인간 시연 의존을 줄임 |

**Probe-Learn-Distill이 residual RL을 쓴다는 점에 주목하십시오 — L5가 L2를 호출합니다.**

**미해결 난점도 명시돼 있습니다** `[문헌]`:
시뮬 기반 RL은 **수백만 회 상호작용**이 필요하고 sim-to-real 격차가 크며, 실물 학습은 **비용이 과도하고 안전 문제**가 있습니다.
flow 기반 VLA의 안정적·효율적 RL 후속학습은 여전히 어렵습니다.

**결론: "사다리 위로 올라가면 끝"은 틀렸습니다.** 파운데이션 모델은 **출발점**이고,
그 위에 다시 RL·residual·증류가 얹힙니다. 앞 문서의 사다리 그림을 이렇게 고쳐 읽으십시오.

---

## 8. 사다리 밖 신흥 축 — 학습된 시뮬레이터·월드 모델

`[문헌]` 사다리의 칸이 아니라 **사다리 전체를 받치는 층**입니다.

| 방향 | 사례 | 값 |
| --- | --- | --- |
| **학습된 동역학** | NeRD — 해석적 솔버의 저수준 동역학·접촉 솔버를 학습 모델로 대체, 실물 데이터로 미세조정 | sim-to-real 격차를 모델 쪽에서 줄임 |
| **신경 시뮬레이터 평가** | RoboWorld — 범용 정책 평가용 빠르고 신뢰 가능한 신경 시뮬레이터. Interactive World Simulator | **실물 평가 비용 절감** |
| **real-to-sim 평가** | 실물 영상에서 **연질체 디지털 트윈**을 만들고 3D Gaussian Splatting으로 렌더. 봉제인형 포장·**로프 라우팅**·T블록 밀기에서 **시뮬 rollout이 실물 성능과 강하게 상관** | 평가 프로토콜의 실질적 대안 |
| 내비게이션 | 3DGS 시뮬 학습 정책이 zero-shot 실물 전이. GRaD-Nav는 **3DGS 렌더의 미분 가능성을 이용해 RL 학습**. SkyJEPA는 잠재 월드 모델로 쿼드로터 zero-shot | 이동체에서 가장 앞서 있음 |

**회의적 시각도 문헌에 있습니다** `[문헌]` — `Robots Need More Than VLAs & World Models` 같은 입장 논문이
이 방향만으로는 부족하다고 주장합니다. **한쪽만 읽지 마십시오.**

**우리에게 직접 값이 있는 지점은 평가입니다.** 로프 라우팅이 3DGS real-to-sim 평가 대상에 이미 들어가 있습니다 —
앞 문서 6.2절 평가 프로토콜의 후속 조사 대상입니다 `[미확인]`.

---

## 9. 실제 산업 배치 — 어디까지 나갔나

**등급을 낮춰 읽으십시오.** 아래는 대부분 **벤더 발표·업계 보도**이고 독립 검증이 없습니다 `[문헌]`.

| 주체 | 내용 |
| --- | --- |
| **AgiBot** | G2 휴머노이드를 **가동 중인 소비자 전자 제조 라인**(Longcheer 태블릿 공장)에 투입. **실물 강화학습(RW-RL)을 활성 라인에 적용한 첫 사례**로 발표 — **수십 분 내 신규 스킬 습득**, 안정 배포 주장. 2026 Q3까지 100대 확대 계획 |
| **BMW × Figure AI** | X3 **30,000대 이상**에 기여, 배치 정확도 **99% 초과** 주장 |
| 기타 | Schaeffler, JAL(하네다 수하물·객실 청소 시험), Toyota, Amazon, Tesla |

**주목할 것은 AgiBot의 RW-RL입니다.** 시뮬이 아니라 **현장에서 RL을 돌린다**는 주장이고,
사실이면 사다리 논의의 전제(시뮬에서 학습 후 이전)가 일부 도메인에서 바뀝니다.
**`[미확인]` 독립 검증이 필요합니다** — 벤더 주장과 재현 가능한 결과는 다릅니다.

---

## 10. 도메인 전반에서 반복되는 운영 원칙 4개

**서로 무관한 도메인에서 같은 결론이 독립적으로 나온 것만 골랐습니다.** 이게 가장 신뢰할 만한 층입니다.

| # | 원칙 | 독립 확인처 |
| --- | --- | --- |
| 1 | **시스템 식별 + 선택적(과하지 않은) 랜덤화** | 드론 5요소 중 4번 · 휴머노이드 비전 조작의 자동 real-to-sim 튜닝 · Lightwheel의 Newton 캘리브레이션 — **3개 도메인** |
| 2 | **특권 정보를 어떤 형태로든 쓴다** | 로코모션 · 휴머노이드 로코조작 · 손재주 촉각 · 관절 도구 · asymmetric critic — **거의 전 도메인** |
| 3 | **컴퓨트 규모가 레시피의 일부다** | VIRAL 최대 64 GPU · Residual MPC의 GPU MPC 100 Hz · 드론 5요소 중 5번(큰 배치) |
| 4 | **평가 절차가 이 분야의 약점이다** | `Deep RL for Robotics: A Survey of Real-World Successes`(Annual Review, Stone 등)가 향후 과제로 **"원칙 있는 개발·평가 절차"**를 명시 · VLA 일반성 벤치마킹 논문 등장 · 신경 시뮬레이터/3DGS 평가 연구 등장 |

**4번이 앞 문서 6.2절의 외부 뒷받침입니다.** 우리만 평가 기준이 없는 게 아니라 **분야 전체의 알려진 약점**이고,
주요 서베이가 과제로 지목한 항목입니다. **간부진의 "주먹구구" 지적은 우리 팀의 문제를 정확히 짚었지만,
동시에 이 분야의 공통 문제이기도 합니다** — 이걸 먼저 정하고 가면 오히려 앞서는 부분이 됩니다.

---

## 11. 앞 문서에 반영해야 할 교정 5건

| # | 앞 문서 위치 | 교정 |
| --- | --- | --- |
| 1 | 2절·0절 톤 | "업계는 맨땅에서 시작하지 않는다" → **"도메인별로 어느 칸에서 시작할지 판단한다."** 로코모션·드론은 맨땅이 표준 |
| 2 | 3절 사다리 구조 | **사다리가 아니라 고리.** L5의 프론티어가 RL 후속학습이고 Probe-Learn-Distill은 residual RL(L2)을 호출 |
| 3 | 3절 L1 | "문헌 용어 없는 약한 칸" → **L1a(상용) / L1b(연구, 실물 전이 미해결)로 분리** |
| 4 | 3절 L2 | 2018 Siemens 프레임 → **Residual MPC로 2026 상태 갱신** |
| 5 | 7절 실행 경로 7·11번 | 2단계 교사-학생 전에 **asymmetric actor-critic을 먼저 시도**하는 분기 추가 |
| 6 | 8절 요청 2번 | GPU 요청을 **"교사 단계까지"**로 한정. 비전 학생이 목표면 규모가 다름 (VIRAL 64 GPU) |

---

## 12. 미확인 — 이 문서의 검증 부채

| # | 확인할 것 |
| --- | --- |
| 1 | **`[문헌]` 전체 원문 대조.** 이 문서는 앞 문서보다 문헌 의존도가 높습니다 |
| 2 | 9절 산업 배치 수치의 독립 검증 — 특히 AgiBot RW-RL의 "수십 분 내 스킬 습득" |
| 3 | L1b 생성형 환경이 **시뮬 내 사전학습·커리큘럼 용도로는 쓸 만한지** (실물 전이는 안 된다는 것이 문헌 평가) |
| 4 | asymmetric actor-critic이 **변형체 태스크**에서도 2단계 증류를 대체할 수 있는지 |
| 5 | PTLD 패턴(어려운 감각을 시뮬하지 않고 실물 데이터로 특권 잠재에 인코딩)을 **변형체 상태 추정**에 적용 가능한지 |
| 6 | 3DGS real-to-sim 평가를 우리 평가 프로토콜에 쓸 수 있는지 — **로프 라우팅이 이미 대상에 있음** |
| 7 | 성숙도 등급 5단계(`[자작]`)가 타당한지 — 외부와 대조해 본 적 없음 |

---

## 13. 참고 문헌

**L0 · 알고리즘**
- [Bridging the Gap: Enabling SAC for High Performance Legged Locomotion (arXiv 2605.24975)](https://arxiv.org/abs/2605.24975) — RSL-RL-SAC. PPO/SAC 격차의 증거
- [RSL-RL: A Learning Library for Robotics Research (arXiv 2509.10771)](https://arxiv.org/abs/2509.10771)
- [What Matters in Learning A Zero-Shot Sim-to-Real RL Policy for Quadrotor Control? (arXiv 2412.11764)](https://arxiv.org/abs/2412.11764) — **드론 5요소**
- [Learning Sim-to-Real Humanoid Locomotion in 15 Minutes (arXiv 2512.01996)](https://arxiv.org/abs/2512.01996)

**L1 · 인프라와 생성형 환경**
- [LeRobot: An Open-Source Library for End-to-End Robot Learning (arXiv 2602.22818)](https://arxiv.org/abs/2602.22818)
- [LeRobot Hub 데이터셋 58,000개 돌파 보도](https://www.techtimes.com/articles/317129/20260525/open-source-robotics-ai-reaches-inflection-point-lerobot-hub-surpasses-58000-datasets-one-year.htm)
- [RoboGen (arXiv 2311.01455)](https://arxiv.org/abs/2311.01455) · [GenSim2 (arXiv 2410.03645)](https://arxiv.org/abs/2410.03645) · [GenDexHand (arXiv 2511.01791)](https://arxiv.org/abs/2511.01791)

**L2 · Residual / 모델 기반 사전지식**
- [Residual MPC: Blending RL with GPU-Parallelized MPC (arXiv 2510.12717)](https://arxiv.org/abs/2510.12717) — **이 칸의 2026 상태**
- [MPC-Guided RL for Scalable Humanoid Control (arXiv 2606.05687)](https://arxiv.org/abs/2606.05687)
- [Residual Reinforcement Learning for Robot Control (arXiv 1812.03201)](https://arxiv.org/abs/1812.03201) — 원류

**L3 · 시연과 데이터**
- [Data Scaling Laws in Imitation Learning for Robotic Manipulation (arXiv 2410.18647)](https://arxiv.org/abs/2410.18647) — **5.1절 전체의 근거**
- [Crossing the Human-Robot Embodiment Gap with Sim-to-Real RL using One Human Demonstration (arXiv 2504.12609)](https://arxiv.org/abs/2504.12609)

**L4 · 특권 정보**
- [VIRAL: Visual Sim-to-Real at Scale for Humanoid Loco-Manipulation (arXiv 2511.15200)](https://arxiv.org/abs/2511.15200) — **64 GPU**
- [PTLD: Sim-to-real Privileged Tactile Latent Distillation (arXiv 2603.04531)](https://arxiv.org/abs/2603.04531) — **+182%**
- [Sim-to-Real RL for Vision-Based Dexterous Manipulation on Humanoids (arXiv 2502.20396)](https://arxiv.org/abs/2502.20396)
- [In-Hand Manipulation of Articulated Tools with Sim-to-Real Transfer (arXiv 2509.23075)](https://arxiv.org/abs/2509.23075)
- [Asymmetric Actor Critic for Image-Based Robot Learning (arXiv 1710.06542)](https://arxiv.org/abs/1710.06542) — **단일 단계 대안**

**L5 · 파운데이션 모델과 RL 후속학습**
- [π0.7: Steerable Generalist Robotic Foundation Model (arXiv 2604.15483)](https://arxiv.org/abs/2604.15483)
- [Benchmarking the Generality of Vision-Language-Action Models (arXiv 2512.11315)](https://arxiv.org/abs/2512.11315)
- [Three Teams, Three Robot Brains — GR00T / Gemini / π 아키텍처 비교](https://blog.pebblous.ai/report/vla-architecture-comparison/en/)
- [VLA-RFT: RL Fine-Tuning with Verified Rewards in World Simulators (arXiv 2510.00406)](https://arxiv.org/abs/2510.00406)
- [RLinf-VLA: Unified and Efficient Framework for RL of VLA (arXiv 2510.06710)](https://arxiv.org/abs/2510.06710)
- [CO-RFT: Chunked Offline RL Fine-Tuning of VLA (arXiv 2508.02219)](https://arxiv.org/abs/2508.02219)
- [Awesome-VLA-Post-Training (모음)](https://github.com/AoqunJin/Awesome-VLA-Post-Training)

**신흥 축 · 월드 모델과 평가**
- [Real-to-Sim Policy Evaluation with Gaussian Splatting of Soft-Body Interactions (arXiv 2511.04665)](https://arxiv.org/abs/2511.04665) — **로프 라우팅 포함**
- [RoboWorld: Neural Simulators for Generalist Robot Policy Evaluation (arXiv 2607.01060)](https://arxiv.org/abs/2607.01060)
- [Robots Need More Than VLAs & World Models (arXiv 2606.06556)](https://arxiv.org/abs/2606.06556) — **반대 입장**
- [Neural Robot Dynamics (NeRD)](https://github.com/NVlabs/neural-robot-dynamics)

**서베이 · 운영**
- [Deep RL for Robotics: A Survey of Real-World Successes (arXiv 2408.03539)](https://arxiv.org/abs/2408.03539) — Annual Review. **10절 4번의 근거**
- [A Survey of Sim-to-Real Methods in RL (arXiv 2502.13187)](https://arxiv.org/abs/2502.13187) · [AwesomeSim2Real](https://github.com/LongchaoDa/AwesomeSim2Real)

**산업 배치** `[문헌]` **— 벤더·보도 근거. 독립 검증 없음**
- [AgiBot, 실물 강화학습 시스템 배치 (The Robot Report)](https://www.therobotreport.com/agibot-deploys-real-world-reinforcement-learning-system/)
- [AGIBOT 휴머노이드 실제 공장 라인 투입](https://interestingengineering.com/ai-robotics/agibot-g2-humanoid-robots-live-production-line)
