# 상용 RL 서베이 — 지금 실제로 팔리고 돌아가는 RL은 어느 수준인가

**이 문서는 "무엇이 가능한가"가 아니라 "무엇이 이미 매출과 운영에 들어가 있는가"입니다.**

> **"어떻게 만들었나"는 [`commercial-rl-architectures.md`](commercial-rl-architectures.md)에 있습니다** —
> 상용 시스템 7개의 관측·정책 구조·행동·학습·보상·안전 계층·결과 수치를 같은 형식으로 정리했습니다.
> **그 문서는 `[논문]` 13 대 `[벤더]` 5로 근거가 훨씬 강합니다** — 아키텍처는 논문에만 적혀 있기 때문입니다.

앞 문서들이 연구·프레임워크 성숙도를 다뤘습니다. **이 문서는 상용화만 봅니다** —
논문 성과, 데모, 전시는 제외하거나 그렇게 표기합니다.

## 표기 규칙

앞 문서들과 같습니다. 다만 **이 문서는 근거 출처의 성격이 결정적이므로 등급을 하나 더 씁니다.**

| 표기 | 뜻 |
| --- | --- |
| `[논문]` | **이 문서에서 추가.** 피어리뷰 논문·기술 보고서 근거 |
| `[벤더]` | **이 문서에서 추가.** 제조사·서비스사 자체 발표. **독립 검증 없음** |
| `[문헌]` | 업계 매체·분석 보도 |
| `[자작]` | 이 문서가 만든 분류·척도 |
| `[미확인]` | 확인해야 하는 것 |

> **앞 서베이의 최대 약점이 이것이었습니다.** 산업 배치 수치를 전부 `[문헌]` 한 등급으로 묶어 놨는데,
> **그 안에 피어리뷰 논문과 보도자료가 섞여 있었습니다.** 이 문서는 분리합니다.
> `[벤더]` 수치는 **마케팅 목적으로 생산된 숫자**이므로 의사결정 근거로 쓰기 전에 반드시 표시하십시오.

### 상용화 등급 `[자작]`

**업계 표준 척도가 아닙니다.** 이 문서가 정한 것입니다.

| 등급 | 뜻 |
| --- | --- |
| **T1** | **제품에 탑재되어 다수 고객에게 출하됨.** 매출이 발생 |
| **T2** | **자사 운영에 대규모 상시 가동.** 판매 제품은 아니지만 실제 프로덕션 |
| **T3** | **유료 파일럿·단일 고객 라인.** 실제 현장이지만 규모가 제한적 |
| **T4** | 데모·전시·연구 발표 |

---

## 0. 결론 — 네 줄

1. **가장 성숙한 상용 RL은 로봇이 아니라 LLM 후속학습입니다** `[논문]`. 규모·매출 기여·재현 절차 전부에서 앞서고, 프론티어 모델 전부가 학습 파이프라인에 RL을 씁니다. **로봇 RL을 논의할 때 이 사실을 기준선으로 잡으십시오**
2. **로봇에서 RL이 확실히 T1인 곳은 저수준 보행 제어입니다** — Spot, ANYmal, Unitree. **제품에 실려 팔립니다**
3. **조작(창고 픽킹)의 상용 성공은 대부분 RL이 아닙니다** — 지도학습·모방학습·파운데이션 모델입니다. **벤더가 "RL"이라고 부르는 것을 그대로 받으면 안 됩니다** (5절)
4. **"RL"이 네 가지 다른 일을 가리킵니다** — 저수준 제어 정책 / 상위 계획·의사결정 / 파라미터·유틸리티 튜닝 / 사전학습 모델 후속학습. **상용화 수준을 물으려면 어느 것인지 먼저 지정해야 합니다** (1절)

**그리고 우리 프로젝트에 직접 걸리는 것** — 우리가 하려는 것(**변형체 조작 × RL**)은
**이 표에서 상용 성숙도가 가장 낮은 교차점**입니다. 상용화된 조작은 대부분 RL이 아니고,
상용화된 RL은 대부분 보행이거나 로봇이 아닙니다 (8절).

---

## 1. 먼저 — "RL"이 가리키는 네 가지

**이 구분 없이는 "상용화 수준"이라는 질문에 답이 안 나옵니다.** 같은 단어가 아주 다른 일을 가리킵니다.

| 종류 | RL이 하는 일 | 상용 성숙도 | 대표 사례 |
| --- | --- | --- | --- |
| **① 저수준 제어 정책** | 관절·추력 목표를 매 스텝 출력 | **T1** | Spot·ANYmal 보행, Atlas |
| **② 상위 계획·의사결정** | 배치·경로·행동 선택 | **T2** | 데이터센터 냉각, 칩 배치 |
| **③ 파라미터·유틸리티 튜닝** | 시스템 계수를 최적화 | **T1/T2** | 광고 입찰, 랭킹 유틸리티 |
| **④ 사전학습 모델 후속학습** | 이미 학습된 모델을 보상으로 개선 | **T1** | LLM RLHF·RLVR |

**②·③은 로봇 제어가 아닙니다.** 그런데 상용 RL 매출·절감액의 대부분이 여기서 나옵니다.
**"RL이 상용화됐다"는 문장은 사실이지만, 그게 ①을 뜻하지는 않습니다.**

---

## 2. ④ LLM 후속학습 — 오늘 가장 큰 상용 RL `[논문]`

**T1. 근거 강함.**

| 항목 | 내용 |
| --- | --- |
| 패러다임 전환 | **RLHF → RLVR.** 선호 정렬(보상 모델 + PPO)에서 **검증 가능한 보상**(결정론적 도구의 이진 피드백)으로 이동 |
| 보상 모델 | RLVR은 **보상 모델이 필요 없습니다** — 정답/오답 직접 피드백 |
| 대표 사례 | **DeepSeek-R1** — 지도 미세조정 없이 base 모델에 **순수 RLVR + GRPO**를 적용해 창발적 추론 |
| | **OpenAI o-시리즈** — 대규모 RL로 학습 |
| 규모 예 | **NVIDIA Nemotron 3 Super** — **21개 검증기 · 37개 데이터셋 · 약 120만 환경 rollout**의 다환경 RL 후속학습 |
| 왜 오래 돌리나 | **검증 가능한 보상은 보상 해킹에 덜 취약**하므로 RLHF보다 훨씬 길게 학습 가능 |

### 2.1 이게 로봇 프로젝트에 주는 것

**보상 해킹 문제의 산업적 해답이 "검증 가능한 보상"으로 정리됐다는 사실입니다.**
앞 서베이 6.5절(보상 거버넌스)에서 "평가 지표를 학습 보상과 분리하라"고 썼는데,
LLM 쪽은 그걸 **보상 자체를 검증 가능한 것으로 바꾸는 방향**으로 풀었습니다.

`[미확인]` **cable 태스크에 이 발상을 옮기면** — "케이블 끝점이 목표 근처"(대리 지표) 대신
**"클립이 실제로 닫혔는가"** 같은 **결정론적으로 검증 가능한 판정**을 보상으로 쓰는 방향입니다.
접촉·체결은 물리적으로 검증 가능한 사건이므로 이 발상이 적용될 여지가 있습니다.

---

## 3. ② 상위 계획 — 두 개의 강한 상용 사례

### 3.1 데이터센터 냉각 (Google) — T2 `[벤더]` + `[문헌]`

| 항목 | 내용 |
| --- | --- |
| 초기 | 냉각 에너지 **최대 40% 절감** (권고 모드, 사람이 실행) |
| 자율 전환 | **"이 규모의 자율 산업 제어 시스템 최초 배치"** — AI가 직접 제어, 운전자 감독 하 |
| 작동 방식 | **5분마다** 수천 센서 스냅샷 → 심층망이 **행동 조합별 미래 에너지 소비 예측** → 안전 제약 만족하며 최소 소비 행동 선택 → **로컬 제어 시스템이 검증 후 실행** |
| 안정 성과 | 광범위 배치 후 **평균 약 30% 냉각 에너지 절감** |
| 플릿 확장 | 2017–2024 전세계 확장 → **사이트 PUE 오버헤드 약 15% 감소** |
| 금액 | 2024년 기준 연 **2~3 TWh** 절감 ≈ **2~3억 달러** (산업용 전력가 기준) |

> **⚠ "이게 RL인가"에 유보를 답니다.** 위 작동 방식은 **예측 모델 + 제약 하 행동 탐색**입니다 —
> 모델 기반 계획에 가깝고, 정책을 보상 경사로 직접 최적화하는 형태로 서술되지 않습니다.
> **성과는 진짜지만 "RL 사례"로 인용할 때는 이 점을 붙이십시오.**
> **이중 검증 구조(로컬 제어가 AI 행동을 검증 후 실행)는 그 자체로 배울 점입니다** — 6절.

### 3.2 칩 배치 (AlphaChip) — T2 `[논문]` + `[벤더]`, **논쟁 있음**

| 항목 | 내용 |
| --- | --- |
| 방식 | 칩 플로어플랜을 **게임처럼** 취급 — 빈 그리드에 회로 블록을 하나씩 배치하는 RL 에이전트 |
| 생산 사용 | **TPU v5e · v5p · Trillium** 여러 세대. 세대가 갈수록 배치 블록 수와 배선 길이 감소폭이 증가 |
| 배포 | 초인적 레이아웃이 **여러 TPU 세대에 tape-out되어 전세계 구글 데이터센터에서 가동** |
| 확산 | Alphabet 내 다른 칩, **외부 칩메이커 — MediaTek 채택** |
| 속도 | 레이아웃을 **몇 시간 내** 생성 |

> **⚠ 재현성 논쟁이 존재합니다.** 이 결과에 대한 회의론과 그에 대한 재반론
> (`That Chip Has Sailed`)이 모두 공개돼 있고, 별도의 논쟁 문서가 정리될 정도입니다.
> **"RL이 상용 반도체 설계를 한다"는 주장의 가장 강한 사례이자 가장 논쟁적인 사례입니다.**
> 회의에서 인용하려면 논쟁 존재를 같이 말하십시오.

---

## 4. ③ 파라미터·유틸리티 튜닝 — 규모가 가장 큼 `[논문]`

**T1/T2. 광고·추천이 상용 RL의 최대 실사용처입니다.**

| 사례 | 수치 |
| --- | --- |
| 프로덕션 규모 | DRL 프레임워크가 **일 200억+ 요청** 서비스 플랫폼에서 평가 |
| 서비스 규모 | 생성형 추천 모델이 **4억+ 사용자**, **500+ QPS**, **<100 ms** 폐루프로 서비스 |
| 매출 효과 | 멀티-DSP 배치에서 **DSP 요청량 34.2% 감소 + 순매출 4.6% 증가** (14일) |
| CTR | `[논문]` **Pinterest DRL-PUT — CTR +9.7%, 30초 이상 클릭 +7.7%** (온라인 A/B, 수동 유틸리티 튜닝 대비). `[문헌]` Meta 내부 시스템 CTR 6.7% 개선 보고 — **출처 등급이 다르므로 Pinterest 수치를 쓰십시오** |
| 프레임워크 | Pinterest — 광고 랭킹 **유틸리티 튜닝** 프로덕션 DRL 프레임워크 |

**그런데 여기서 RL이 하는 일은 "제어"가 아닙니다** — **랭킹 유틸리티 계수 튜닝, 입찰가 최적화**입니다.
로봇 정책 학습과는 문제 구조가 다릅니다.

`[논문]` **한계도 명시돼 있습니다** — 희소 광고 시나리오에서 오프라인 RL은 **과대추정·분포 이동·예산 제약
무시** 문제를 겪고, **"프로덕션 유틸리티 튜닝에서 RL 구현이 off-the-shelf 채택처럼 간단한 적은 없다"**고
직접 적혀 있습니다.

---

## 5. ① 로봇 저수준 제어 — 여기가 진짜 로봇 RL 상용 지점

### 5.1 4족 보행 — T1, 근거 강함

| 주체 | RL 사용 | 상용 규모 |
| --- | --- | --- |
| **Boston Dynamics Spot** | `[벤더]` **RL을 Spot 보행 제어 시스템에 통합** — 시간이 지나며 확장 가능한 제어 소프트웨어를 만들기 위해 | `[문헌]` **1,500대 이상, 40개국 이상** |
| **ANYbotics ANYmal** | ETH Zurich 계보 — 교사-학생 증류 보행의 원류 | `[문헌]` 상용 주문 개시. **ANYmal X는 폭발위험 환경 인증**, **PETRONAS 해양 플랫폼 배치** |
| **Unitree** | `[벤더]` 제품 페이지가 **G1은 "모방 및 강화학습으로 구동"**된다고 명시. `unitree_rl_gym`으로 Go2·H1·G1용 RL 구현 공개 | `[문헌]` **2025년 5,500대+ 출하**, 2026년 1~2만 대 목표 |

**결론: 4족 보행은 RL 제어기가 제품에 실려 팔리는 단계입니다.** 이 문서에서 ①이 T1인 유일한 확실한 영역입니다.

### 5.2 휴머노이드 — 2026이 T4 → T1 전환점

**가장 강한 증거가 Boston Dynamics Atlas입니다.**

| 항목 | 내용 |
| --- | --- |
| 생산 상태 | `[벤더]` **2026년 1월 생산형 Atlas 공개** (Hyundai Motor Group과) |
| 배정 | `[문헌]` **2026년 생산분 전량이 이미 배정** — Hyundai RMAC(로보틱스 메타플랜트 응용센터)과 **Google DeepMind**로 출하 예정 |
| 투자 | `[문헌]` 260억 달러 투자, 3만 대 규모 휴머노이드 공장 |
| **RL 위치** | `[벤더]` **"Atlas 새 스킬의 핵심은 전통적 스크립트 컨트롤러가 아니라 RL 정책"** — 가상 세계에서 보상 기반 시행착오로 움직임을 학습 |
| 학습 구성 | `[벤더]` **시뮬 RL + 원격조작 시연 혼합** |

**나머지는 아직 파일럿입니다** `[문헌]`:

| 주체 | 상태 |
| --- | --- |
| Unitree | 2025년 **5,500대+** 출하, 2026년 **1~2만 대** 목표 — 물량은 중국이 앞섬 |
| Tesla Optimus Gen 3 | Fremont 생산 개시, **초기 약 1,000대** |
| BMW · Mercedes · Hyundai | **파일럿. "수천이 아니라 수십 대 규모"** — BMW 라이프치히 공장, Mercedes는 Apollo로 부품 운반·초기 품질 검사 |
| AgiBot | `[벤더]` 가동 라인에 **현장 RL(RW-RL)** 적용 주장, 수십 분 내 신규 스킬 습득 — **독립 검증 없음** |

**읽는 법**: `[벤더]` "Atlas 핵심이 RL 정책"은 제조사 기술 블로그이고, `[문헌]` "생산분 전량 배정"은 업계 보도입니다.
**둘 다 독립 검증은 아니지만, 생산 배정은 상업적 약속이므로 데모보다 무게가 있습니다.**

### 5.3 자율주행 — T2, 그런데 RL은 부분 역할 `[벤더]`

| 항목 | 내용 |
| --- | --- |
| RL 위치 | **제어에 RL + MPC를 신경 정책과 혼성.** 주행 정책 전체가 RL인 것이 아님 |
| 추가 용도 | **행동 모델 폐루프 RL 미세조정** — 충돌률 등 목표 지표 개선 (Waymo Open Sim Agents challenge) |
| 운영 규모 | 2025년 말 기준 **주당 45만+ 유료 승차**, **9,600만 자율 마일**, 인간 대비 **3.5배** 안전한 충돌 회피 |

**즉 세계 최대 자율 이동 서비스에서도 RL은 스택의 한 부품**입니다. 이것이 ①의 현실적 형태입니다 —
**전부 RL로 가는 게 아니라 고전 제어와 섞습니다.** 앞 서베이의 L2a·L2b가 여기서 재확인됩니다.

---

## 6. 창고 픽킹 — 상용은 성공했는데 그게 RL이 아닙니다

**이 절이 이 문서에서 가장 조심해야 할 부분입니다.**

| 주체 | 상용 규모 | **실제 기법** |
| --- | --- | --- |
| **Covariant** | `[문헌]` **RFM-1**(80억 파라미터)이 **100대 이상 창고 로봇 팔**에서 가동, **수천만 픽 궤적** 학습, **구독 매출**. 미국·유럽·APAC. 의류·제약·전자·3PL. Amazon이 **비독점 라이선스 + 인력 영입** | 마케팅은 "deep RL"이라 하지만 **RFM-1은 파운데이션 모델** |
| **Amazon Robin** | `[벤더]` 팔 **1,000대+**, **일 최대 500만 패키지** 단품화, 평가 기간 **2억+ 패키지** 처리 | `[논문]` 논문 제목이 **"Learned Metrics of Pick Success"** — **지도학습** |
| **Amazon Vulcan** | `[벤더]` FC 보관 품목의 **약 75%** 픽·스토우. 스포캔 완전 가동, 함부르크 시험 | `[벤더]` **"실세계 창고 데이터로 학습"** — IL·지도학습 계열 |
| **Amazon 전체** | `[벤더]` 로봇 **75만~100만 대** 배치. DeepFleet은 플릿 조율용 **생성형 AI 파운데이션 모델** | 조율·예측 모델 |

**결론: 창고 조작의 상용 성공은 대부분 지도학습·모방학습·파운데이션 모델입니다.**

그리고 `[문헌]` **한계가 명시돼 있습니다** — **전체 SKU 범위에서 사람 피커를 완전히 대체할 신뢰도는 여전히 미해결**입니다.

> **이것이 이 서베이의 가장 실용적인 경고입니다.** "조작 로봇이 상용화됐다"는 사실에서
> **"조작 RL이 상용화됐다"를 도출하면 안 됩니다.** 벤더 표현은 근거가 아닙니다 —
> 논문 제목과 학습 방식 설명을 확인하십시오.

---

## 7. 공정 제어 — 최초 대규모 상용 사례가 나왔습니다

**T1 진입. 그리고 이 절의 근거가 `[논문]`이라 무게가 다릅니다.**

| 항목 | 내용 |
| --- | --- |
| 사례 | `[논문]` **19만 배럴 원유 증류탑(CDU) 압력 제어 RL — "업계 최초 전규모 상용 배치"** |
| 성과 | **운전자 개입 시간 84% 감소**, **누적 오차 12.8% 감소** |
| HVAC | `[문헌]` 규칙 기반 대비 **에너지 10~30% 절감** 보고. 자율 HVAC 제어에서 **가장 활발히 특허되는 접근** 중 하나 |
| ROI | `[문헌]` 처리량·수율 **1~5% 개선** 기대 → 연 10억 달러 규모 정제소면 **연 1,000만~5,000만 달러** |

### 7.1 도입 요구사항 — 우리 운영 규율과 그대로 겹칩니다 `[문헌]`

**상용 배치에 필요하다고 명시된 것들입니다.**

| 요구사항 | 우리 서베이의 대응 |
| --- | --- |
| **고충실도 공정 시뮬레이터** | Newton·Isaac Lab 선택 자체 |
| **다중 운전영역 이력 데이터** | 6.4절 시스템 식별 |
| **DCS 통합** | 실물 이전 (G5) |
| **AI 권고를 수용하는 제어실 운전자 워크플로** | **우리 문서에 없던 항목** |

**마지막 줄이 중요합니다.** 상용 RL의 도입 장벽에 **"사람이 그 출력을 받아들이는 절차"**가 들어 있습니다.
Google 냉각도 같은 구조입니다 — **로컬 제어 시스템이 AI 행동을 검증한 뒤 실행**하고 운전자가 감독합니다.

`[자작]` **우리 게이트 체계에 이 층이 없습니다.** G5(실물 이전)를 "성공률·사이클 타임"으로만 정의했는데,
상용 사례들은 **검증 계층 + 사람 수용 절차**를 별도 요구사항으로 둡니다. **게이트를 하나 더 두는 것이 맞습니다.**

---

## 8. 우리 프로젝트가 서 있는 자리

**위 조사를 우리 좌표에 찍으면 이렇습니다.**

| | RL로 상용화됨 | RL이 아닌 방법으로 상용화됨 |
| --- | --- | --- |
| **보행·이동** | **✅ T1** — Spot, ANYmal, Unitree | — |
| **강체 조작 (픽킹)** | ❌ 거의 없음 | **✅ T1/T2** — 지도학습·IL·파운데이션 모델 |
| **접촉 많은 조립** | ⚠ T3 파일럿 (Skild AI 등, `[벤더]`) | 전통 자동화·티칭 |
| **변형체 조작 (우리 목표)** | ❌ **상용 사례 없음** | ⚠ 삼성·Lightwheel이 `[벤더]` 수준 |
| 비로봇 (계획·튜닝·LLM) | **✅ T1/T2** — 규모가 가장 큼 | — |

**우리는 표에서 가장 빈 칸을 목표로 하고 있습니다.** 이건 나쁜 뜻이 아니라 **일정과 기대치의 근거**입니다.

### 8.1 그래서 실무적으로 따라오는 것 세 가지 `[자작]`

1. **"상용 선례가 있다"는 주장을 조심하십시오.** 5절 삼성·Skild 사례는 전부 `[벤더]` 등급입니다.
   변형체 조작 RL의 **피어리뷰된 상용 배치 사례는 이 조사에서 찾지 못했습니다**
2. **가장 안전한 경로는 혼성입니다.** 상용화된 ①은 전부 고전 제어와 섞여 있습니다 —
   Waymo는 RL+MPC 혼성, Isaac Lab 기본값은 RL+PD. **저수준은 고전 제어, RL은 그 위, 상위 단계는 스크립트·IL**
3. **검증 계층과 사람 수용 절차를 게이트에 넣으십시오** (7.1절). 상용 사례들이 공통으로 요구합니다

---

## 9. 미확인 — 이 문서의 검증 부채

| # | 확인할 것 |
| --- | --- |
| 1 | **`[벤더]` 항목 전부.** 특히 Atlas의 "RL 정책이 핵심"과 AgiBot RW-RL |
| 2 | Boston Dynamics Spot의 RL이 **출하 제품 펌웨어에 들어간 것인지, 옵션·후속 릴리스인지** |
| 3 | Covariant RFM-1의 학습에 **RL이 실제로 얼마나 쓰이는지** — 파운데이션 모델과 RL의 비중 |
| 4 | AlphaChip 재현성 논쟁의 현재 결론 |
| 5 | Google 냉각이 **정책 최적화인지 모델 기반 계획인지** — 원문 확인 |
| 6 | CDU 압력 제어 논문(전규모 상용 최초)의 **실제 알고리즘과 안전 구조** — 7절 요구사항 목록의 출처 |
| 7 | 변형체 조작의 **피어리뷰된 상용 배치 사례가 정말 없는지** — 없다는 주장은 검색 한계일 수 있음 |
| 8 | 상용화 등급 T1~T4(`[자작]`)가 타당한지 |

---

## 10. 참고 문헌

**LLM 후속학습 (2절)**
- [The State of Reinforcement Learning for LLM Reasoning (Raschka)](https://magazine.sebastianraschka.com/p/the-state-of-llm-reasoning-model-training) — RLHF → RLVR 전환 정리
- [DeepSeek-R1 (arXiv 2501.12948)](https://arxiv.org/abs/2501.12948) — 순수 RLVR + GRPO
- [Mastering Agentic Techniques: AI Agent RL (NVIDIA)](https://developer.nvidia.com/blog/mastering-agentic-techniques-ai-agent-reinforcement-learning/) — Nemotron 3 Super 후속학습 규모
- [OpenRLHF (arXiv 2405.11143)](https://arxiv.org/abs/2405.11143)

**상위 계획 (3절)**
- [Safety-first AI for autonomous data centre cooling and industrial control (DeepMind)](https://deepmind.google/blog/safety-first-ai-for-autonomous-data-centre-cooling-and-industrial-control/) — **자율 제어 전환·검증 구조**
- [DeepMind AI Reduces Google Data Centre Cooling Bill by 40%](https://deepmind.google/blog/deepmind-ai-reduces-google-data-centre-cooling-bill-by-40/)
- [Google just gave control over data center cooling to an AI (MIT Tech Review)](https://www.technologyreview.com/2018/08/17/140987/google-just-gave-control-over-data-center-cooling-to-an-ai/)
- [How AlphaChip transformed computer chip design (DeepMind)](https://deepmind.google/blog/how-alphachip-transformed-computer-chip-design/) — TPU v5e·v5p·Trillium
- [AlphaChip (controversy) — Wikipedia](https://en.wikipedia.org/wiki/AlphaChip_(controversy)) · [That Chip Has Sailed (arXiv 2411.10053)](https://arxiv.org/abs/2411.10053) — **논쟁 양쪽**

**광고·추천 (4절)**
- [Deep RL for Ranking Utility Tuning in the Ad Recommender System at Pinterest (arXiv 2509.05292)](https://arxiv.org/abs/2509.05292)
- [A Production-Ready RL Framework for Personalized Utility Tuning (arXiv 2605.16344)](https://arxiv.org/abs/2605.16344)
- [Generative Recommendation for Large-Scale Advertising (arXiv 2602.22732)](https://arxiv.org/abs/2602.22732)
- [Multi-task Offline RL for Online Advertising (KDD 2025)](https://dl.acm.org/doi/10.1145/3711896.3737250)

**로봇 저수준 제어 (5절)**
- [Starting on the Right Foot with Reinforcement Learning (Boston Dynamics)](https://bostondynamics.com/blog/starting-on-the-right-foot-with-reinforcement-learning/) — **Spot 보행에 RL 통합**
- [Atlas' Evolution From Research Robot to Industrial Humanoid (Boston Dynamics)](https://bostondynamics.com/blog/atlas-evolution-from-research-robot-to-industrial-humanoid/)
- [CES 2026: Boston Dynamics Set to Ship First Atlas Humanoids This Year (A3)](https://www.automate.org/robotics/industry-insights/boston-dynamics-to-begin-production-on-redesigned-atlas-humanoid-in-2026)
- [ANYbotics opens commercial orders for ANYmal (The Robot Report)](https://www.therobotreport.com/anybotics-opens-commercial-order-for-anymal-quadruped/)
- [Quadruped State of the Market (SemiAnalysis)](https://newsletter.semianalysis.com/p/quadruped-state-of-the-market-unitree) — Spot 1,500대+
- [unitreerobotics/unitree_rl_gym](https://github.com/unitreerobotics/unitree_rl_gym)
- [Humanoid robotics in 2026: pilots, pricing, and reality (HumanoidHub)](https://www.humanoidhub.ai/blog/humanoid-robotics-2026-pilots-production-what-s-real-what) — **파일럿 vs 생산 구분**
- [Improving Agent Behaviors with RL Fine-tuning for Autonomous Driving (Waymo)](https://waymo.com/research/improving-agent-behaviors-with-rl-fine-tuning-for-autonomous-driving/)

**창고 픽킹 (6절)**
- [Demonstrating Large-Scale Package Manipulation via Learned Metrics of Pick Success (arXiv 2305.10272)](https://arxiv.org/abs/2305.10272) — **Amazon Robin. 지도학습**
- [Introducing Vulcan: Amazon's first robot with a sense of touch](https://www.aboutamazon.com/news/operations/amazon-vulcan-robot-pick-stow-touch)
- [Amazon hires from Covariant, licenses technology](https://www.aboutamazon.com/news/company-news/amazon-covariant-ai-robots)
- [Covariant's RFM-1 Monetizes Warehouse Picking (Sacra)](https://sacra.com/chat/h/5b30dd6f-3e27-4d76-973e-74f3faf26fb9/) — 100대+ 팔, 구독 매출

**공정 제어 (7절)**
- [Implementation of RL for enhanced pressure control in a 190,000-barrel crude distillation unit: the first full-scale commercial deployment (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0952197625009078) — **이 문서에서 근거가 가장 강한 상용 제어 사례**
- [RL for Chemical Reactor Control: Beyond MPC & PID](https://f7i.ai/blog/reinforcement-learning-for-chemical-reactor-control-how-to-optimize-yield-while-extending-asset-life) — ROI·도입 요구사항
- [The Challenges of Using RL for Controlling Industrial Energy Systems (arXiv 2605.31044)](https://arxiv.org/abs/2605.31044) — **반대편 근거. 같이 읽으십시오**
- [Deep RL for HVAC Optimization 2026 (PatSnap)](https://www.patsnap.com/resources/blog/rd-blog/deep-reinforcement-learning-for-hvac-optimization-2026/)
