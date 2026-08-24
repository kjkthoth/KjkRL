# 학습 실행의 해부 — 지금 RL이 어떤 식으로 돌아가는가

**이 문서는 "무엇을 학습시킬까"가 아니라 "학습 한 번이 실제로 어떤 구조로 돌아가는가"입니다.**

`rl-operations-survey.md`가 착수 지점을, `ladder-maturity-survey.md`가 도메인별 성숙도를 다룹니다.
이 문서는 그 아래층 — **실행 단위의 구조**입니다. 태스크를 확정하기 전에 이걸 먼저 봐야 하는 이유는
**태스크 선택이 실행 구조의 어느 모드로 들어갈지를 결정하기 때문**입니다 (2절).

표기 규칙은 앞 문서들과 같습니다. `[문헌]` 검증 한계도 동일합니다 — **원문 직접 열람이 egress로 차단된
환경에서 작성됐고 1차 대조를 하지 않았습니다.**

---

## 0. 요약

1. **엔트리포인트 5개가 곧 지형도입니다** `[실측]`. Isaac Lab 3.0의 통합 학습 진입점은 `--rl_library` 값으로
   5개 스크립트에 분기합니다: `rsl_rl` `rl_games` `skrl` `sb3` `rlinf`
2. **그 5개는 두 가지 모드입니다.** 앞 4개는 **정책을 처음부터 학습**, `rlinf`는 **사전학습된 VLA를 RL로 후속학습**.
   즉 **사다리 L0~L4와 L5-고리가 같은 CLI 뒤에 나란히 있습니다**
3. **`rlinf`는 우리 체크아웃에 지금 설치돼 있지 않습니다** `[실측]` — `contrib` extra가 필요하고 `il -i`가 건너뜁니다
4. **실행 1 iteration의 구조는 어느 라이브러리든 같습니다** — 롤아웃 수집 → 미니배치 분할 → 여러 epoch 갱신.
   `[실측]` 우리 cartpole 로그의 "iteration당 0.36초"가 이 한 바퀴입니다

---

## 1. 엔트리포인트가 말해 주는 것 `[실측]`

Isaac Lab 3.0의 통합 진입점 구조입니다.

```python
LIBRARY_ENTRYPOINTS = {
    "rl_games": SCRIPT_DIR / "rl_games" / "train_rl_games.py",
    "rlinf":    SCRIPT_DIR / "rlinf"    / "train_rlinf.py",
    "rsl_rl":   SCRIPT_DIR / "rsl_rl"   / "train_rsl_rl.py",
    "sb3":      SCRIPT_DIR / "sb3"      / "train_sb3.py",
    "skrl":     SCRIPT_DIR / "skrl"     / "train_skrl.py",
}
```

**이 딕셔너리가 이 프로젝트에서 선택 가능한 학습 방식의 전부입니다.** 그리고 `train.bat`이 이미 그 스위치를 노출합니다 `[실측]`.

```
set RL_LIBRARY=skrl     rem train.bat 헤더에 문서화된 방식
```

즉 **라이브러리 교체는 코드 수정이 아니라 환경변수 한 줄**입니다. 래퍼가 이미 그렇게 설계돼 있습니다.

---

## 2. 두 가지 모드 — 이게 태스크 확정 전에 봐야 하는 이유

| 모드 | 라이브러리 | 무엇을 학습하는가 | 사다리 |
| --- | --- | --- | --- |
| **A. 정책을 처음부터** | `rsl_rl` `rl_games` `skrl` `sb3` | 무작위 초기화 정책 → 보상으로 수렴 | L0 · L1 · L2 · L4 |
| **B. 사전학습 VLA 후속학습** | **`rlinf`** | **이미 학습된 VLA 가중치를 RL로 개선** | **L5 + 고리** |

**모드가 다르면 필요한 것이 전부 다릅니다.**

| | 모드 A | 모드 B |
| --- | --- | --- |
| 관측 | 상태 벡터로 충분 | **카메라 필수** (VLA가 vision-language-action) |
| 초기 가중치 | 없음 | **사전학습 체크포인트 필요** |
| 데이터 | 없음 | 사전학습은 이미 됨. 후속학습은 시뮬 상호작용 |
| 보상 | 조밀하게 설계 필요 | **태스크 성공 신호 위주** — 정책이 자기 데이터를 모음 `[문헌]` |
| 우리 스택 | 지금 됩니다 `[실측]` | Isaac Sim + `contrib` extra 필요 |

**태스크를 확정하면 모드가 사실상 결정됩니다.** 커넥터 삽입을 상태 기반으로 정의하면 모드 A,
"사람이 말로 지시하는 케이블 정리"로 정의하면 모드 B입니다. **순서가 거꾸로 되면 안 됩니다** —
태스크를 먼저 확정하고 모드를 따라가야, 모드를 먼저 고르고 태스크를 억지로 맞추는 일이 없습니다.

### 2.1 모드 B의 실체 — RLinf `[문헌]`

**RLinf는 Embodied·Agentic AI용 RL 인프라이고, Isaac Lab에 공식 통합돼 있습니다.**

| 항목 | 내용 |
| --- | --- |
| 지원 VLA | OpenVLA, OpenVLA-OFT, π0, π0.5, **GR00T** |
| 알고리즘 | **GRPO, PPO** |
| 지원 시뮬 | ManiSkill, LIBERO, RoboTwin, **IsaacLab**, CALVIN |
| 실물 | Franka, XSquare Turtle2 |
| 보고 성능 | LIBERO·ManiSkill·RoboTwin에서 **약 20~85% 개선** |

`[문헌]` Isaac Lab 문서의 실행 예시입니다.

```
uv run isaaclab train --rl_library rlinf --config_name isaaclab_ppo_gr00t_assemble_trocar
```

**`assemble_trocar`를 눈여겨보십시오** — 트로카(수술 기구) **조립** 태스크에 GR00T + PPO입니다.
`[미확인]` 접촉이 많은 조립이라는 점에서 우리 관심(커넥터 삽입)과 성질이 겹칩니다. **참조 config로 확인 대상입니다.**

### 2.2 지금 우리 스택에서 모드 B가 막힌 지점 `[실측]`

README 3절에 이미 기록돼 있습니다 — `il -i`가 설치하는 목록에서 **`contrib`는 수동 대상이라 빠지고,
그 `contrib` extra가 `rlinf` 전용**입니다.

**즉 모드 B는 "안 되는 것"이 아니라 "아직 안 깐 것"입니다.** 변형체(`isaaclab_contrib.deformable`)는
core 서브모듈이라 이미 설치돼 있으니, 여기서 필요한 건 extra 하나입니다 `[미확인]` — 실제 설치 명령과
의존성 충돌 여부는 확인해야 합니다.

---

## 3. 실행 1 iteration의 구조 — 라이브러리와 무관하게 같습니다

`[문헌]` 온폴리시(PPO 계열) 한 iteration의 골격입니다.

```
  1. 롤아웃 수집    모든 병렬 env를 horizon 스텝만큼 진행
                    → 배치 = num_envs × horizon
  2. 미니배치 분할  배치를 셔플해 num_mini_batches 개로 나눔
  3. 갱신           num_learning_epochs 번 반복
                    → 총 그래디언트 갱신 = epochs × mini_batches
  4. 로깅·체크포인트
```

**전형적인 값** `[문헌]`:

| 파라미터 | 값 | 뜻 |
| --- | --- | --- |
| horizon (env당 스텝) | **16~32** | 한 iteration에 env마다 몇 스텝 굴리는가 |
| `num_mini_batches` | 4 | 배치를 몇 조각으로 나누는가 |
| `num_learning_epochs` | 5 | 같은 데이터를 몇 번 재사용하는가 |
| → 그래디언트 갱신/iteration | **5 × 4 = 20** | |

`[문헌]` **병렬 env 수가 적을 때는 배치나 horizon을 키워 보정합니다** — 수집 데이터가 적은 것을 상쇄하는 방향입니다.
**8GB 머신에서 `--num_envs`를 낮출 때 같이 봐야 하는 항목입니다** `[미확인]`.

### 3.1 우리 로그와 연결 `[실측]`

README 4.3의 cartpole 실측이 이 구조의 실제 값입니다.

| 구간 | 시간 | 이 절과의 대응 |
| --- | --- | --- |
| Initialize solver | 33.5초 | iteration 밖. 1회성 |
| CUDA graph | 32.9초 | iteration 밖. 1회성 |
| **학습 10 iteration** | **10.05초** | **위 1~4번을 10바퀴** |
| iteration당 | **0.36~0.37초** (첫 회만 1.77초) | **한 바퀴 = 롤아웃 + 20회 갱신** |

**첫 iteration만 1.77초인 이유가 여기서 설명됩니다** — 커널·그래프 워밍업이 첫 바퀴에 섞입니다.
**즉 iteration 수를 늘려야 의미 있는 처리량 수치가 나옵니다.** README 5.4("벽시계는 속도 지표가 아니다")의 구체형입니다.

### 3.2 처리량을 보고할 때 `[자작]`

앞 문서 6.2절 평가 프로토콜에 붙는 실무 규칙입니다.

- **step/s를 `num_envs`와 함께** 적으십시오. env 수 없는 step/s는 비교 불가입니다
- **첫 iteration을 제외**하고 계산하십시오
- **초기화 시간을 따로** 적으십시오. 짧은 실행에서는 그게 측정값의 대부분입니다

---

## 4. 라이브러리 선택 — 근거가 공식 문서에 있습니다

`[문헌]` Isaac Lab 문서에 **RL 라이브러리 비교** 페이지가 있고, **동일한 `Isaac-Humanoid-v0` 환경 ·
단일 RTX 4090 · 65.5M 스텝**에 대해 라이브러리별 총 학습 시간을 실측해 둔 벤치마크가 있습니다.

**추측으로 고르지 마십시오 — 이 표를 보고 고르십시오.** README 6.4의 솔버 선택 원칙과 같습니다.

| 라이브러리 | 성격 `[문헌]` |
| --- | --- |
| **`rsl_rl`** | **다리형 로코모션 공개 코드가 대부분 이걸 씁니다.** 우리 기본값 `[실측]` |
| `skrl` | 모듈식·확장 지향. 널리 쓰이는 RL 기법의 표준 구현 제공 |
| `rl_games` | Isaac Lab 생태계 통합. iteration마다 FPS 등 통계 출력 |
| `sb3` | 범용 호환성이 넓음 |
| **`rlinf`** | **VLA 후속학습 전용** (2.1절) |

**우리 선택은 유지가 맞습니다** — 변형체 태스크가 `FrankaDeformablePPORunnerCfg`(rsl_rl)로 이미 구성돼
있으므로 `[실측]`, 라이브러리를 바꾸면 그 참조 구현을 버립니다.

---

## 5. 알고리즘 지형 — PPO가 기본인 이유와 GRPO가 등장한 이유

### 5.1 PPO `[문헌]`

앞 문서에서 정리한 대로 다리형 로봇의 de facto 표준이고, **널리 쓰이는 프레임워크가 PPO만 지원하는 경우가
많습니다.** 온폴리시를 대규모 병렬 env로 올리기 쉬운 것이 이유입니다.

### 5.2 GRPO — 가치망을 없앱니다 `[문헌]`

`rlinf`가 PPO와 함께 제공하는 알고리즘입니다.

| | PPO | GRPO |
| --- | --- | --- |
| 필요한 모델 | 정책 + **가치망** | **정책만** |
| 이득 기준선 | 가치망 추정 | **그룹 평균 보상** — 입력마다 K개 후보를 샘플링해 그룹 평균을 기준선으로 |
| 이점 | | 가치망 오버헤드 제거, 가치 추정 부정확성 회피. **대규모 VLA 학습에 유리** |

**그런데 반대 보고도 있습니다** `[문헌]` — **VLA에서는 DPO·GRPO 같은 LLM 유래 기법보다 PPO가 더
효과적이라는 지적**이 있습니다. Isaac Lab 예제 config 이름도 `isaaclab_ppo_gr00t_...` 로 **PPO**입니다.

**실무 결론** `[자작]`: **모드 B로 가더라도 PPO부터 시작하십시오.** GRPO는 가치망 비용이 실제로 병목이라고
측정된 뒤에 검토할 항목입니다. 5.1절과 같은 논리입니다 — **기본값을 이기려면 근거가 있어야 합니다.**

---

## 6. 레벨 갱신 — 요청 우선 1 승인의 효과

**Isaac Sim 6.0.1 설치가 승인됐으므로 사다리 가용성이 바뀝니다** `[문서]`.

| 칸 | 승인 전 | 승인 후 |
| --- | --- | --- |
| L0 · L1 · L2 | 가능 | 가능 |
| **L3** 시연 기반 (teleop · mimic) | **불가** | **가능** — kitless가 포기했던 워크플로가 열립니다 |
| **L4** 교사-학생 | 부분 (비카메라 학생만) | **완전** — RTX 렌더가 붙으면 비전 학생이 가능 |
| **L5** 파운데이션 모델 | **불가** | **가능** — 카메라 + `rlinf` (`contrib` extra 필요) |

**즉 앞 문서들의 "L3·L5 잠김"은 해소됐습니다.** 두 문서에 이 갱신을 반영했습니다.

**다만 열린 것과 할 수 있는 것은 다릅니다.** L4의 비전 학생은 `[문헌]` VIRAL이 최대 64 GPU를 쓴 규모이고,
우리는 Titan RTX 1장입니다. **열렸다는 것은 "구조적으로 막히지 않는다"는 뜻이고, 규모는 별개 제약입니다.**

---

## 7. 우선 2(태스크 확정) 전에 확인할 것

**전부 코드를 안 쓰고 확인 가능한 것들입니다.**

| # | 확인 | 왜 지금 |
| --- | --- | --- |
| 1 | **Isaac Lab RL 라이브러리 비교 벤치 표** 실제 수치 (4090/65.5M 스텝) | 라이브러리 선택 근거. 4절 |
| 2 | **`isaaclab_ppo_gr00t_assemble_trocar` config 내용** | 접촉 조립 태스크의 참조 구성. 2.1절 |
| 3 | **`contrib` extra 설치 명령과 의존성 충돌 여부** | 모드 B 진입 조건. 2.2절 |
| 4 | Isaac Lab **Debugging and Training Guide** 문서 | 실행이 안 될 때의 공식 절차 `[미확인]` |
| 5 | 승인된 Isaac Sim 설치 후 **mimic/teleop이 실제로 열리는지** | 6절 표의 `[문서]`를 `[실측]`으로 올리는 일 |
| 6 | 태스크 후보 3종을 **모드 A/B로 각각 정의해 보기** | 2절 — 태스크가 모드를 결정하는지 확인 |

**6번이 우선 2의 실제 내용입니다.** "커넥터 삽입 / 클립 라우팅 / 채널 안착" 중 하나를 고르는 것으로 보이지만,
**같은 태스크도 관측을 어떻게 정의하느냐에 따라 모드가 갈립니다.** 태스크 이름만 고르고 넘어가면
그 결정이 나중에 암묵적으로 내려집니다.

---

## 8. 참고 문헌

**Isaac Lab 실행 구조**
- [Reinforcement Learning Library Comparison](https://isaac-sim.github.io/IsaacLab/main/source/overview/reinforcement-learning/rl_frameworks.html) — **4절 벤치의 출처**
- [Debugging and Training Guide](https://isaac-sim.github.io/IsaacLab/main/source/overview/reinforcement-learning/training_guide.html)
- [Training with an RL Agent (튜토리얼)](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/run_rl_training.html) · [Configuring an RL Agent](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/configuring_rl_training.html)
- [isaaclab_rl API](https://isaac-sim.github.io/IsaacLab/main/source/api/lab_rl/isaaclab_rl.html)
- [Isaac Lab 프레임워크 논문 (arXiv 2511.04831)](https://arxiv.org/abs/2511.04831)

**모드 B — VLA 후속학습**
- [RL Post-Training for VLA Models (Isaac Lab 문서)](https://isaac-sim.github.io/IsaacLab/develop/source/experimental-features/rlinf_vla_posttraining.html) — **2.1절 실행 예시의 출처**
- [RLinf/RLinf (GitHub)](https://github.com/RLinf/RLinf) · [RLinf 문서](https://rlinf.readthedocs.io/) · [RL with IsaacLab Benchmark](https://rlinf.readthedocs.io/en/latest/rst_source/examples/isaaclab.html)
- [RLinf-VLA (arXiv 2510.06710)](https://arxiv.org/abs/2510.06710)
- [πRL: Online RL Fine-tuning for Flow-based VLA (arXiv 2510.25889)](https://arxiv.org/abs/2510.25889)
- [What Can RL Bring to VLA Generalization? An Empirical Study (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/115842)

**알고리즘**
- [DeepSeek-R1 (arXiv 2501.12948)](https://arxiv.org/abs/2501.12948) — GRPO 원류
- [Reinforcement Learning for Flow-Matching Policies (arXiv 2507.15073)](https://arxiv.org/abs/2507.15073)
