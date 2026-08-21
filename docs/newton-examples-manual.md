# Newton 예제 실행 매뉴얼

Newton 1.2.1 / Isaac Lab 3.0.0-beta2 kitless / Windows

이 문서는 **Newton에 들어 있는 예제를 실행하고 인자로 조절하는 방법**만 다룹니다.
설치·환경 구성은 `README.md`, RL 태스크 학습은 `README.md` 6절을 보십시오.

---

## 1. 전제

| 항목 | 값 |
| --- | --- |
| Newton | 1.2.1 (`newton[examples]` 포함) |
| 예제 수 | 68개 |
| 실행 진입점 | `python -m newton.examples` |
| 래퍼 | 리포 루트의 `il.bat` — 경로·venv·uv를 맞춰 줍니다 |

리포 루트에서 `il.bat`으로 부릅니다. venv를 직접 활성화했다면 `python -m newton.examples ...`도 동일합니다.

---

## 2. 실행 — 3가지 형태

### 2.1 목록 보기

```powershell
.\il.bat -p -m newton.examples --list
```

### 2.2 예제 실행

```powershell
.\il.bat -p -m newton.examples cloth_hanging
```

인자를 주지 않으면 `basic_pendulum`이 돕니다.

### 2.3 예제별 인자 확인

```powershell
.\il.bat -p -m newton.examples cloth_hanging --help
```

**예제마다 인자가 다릅니다.** 공통 인자에 예제 고유 인자가 더해진 형태입니다.

---

## 3. 보는 방법 — 가장 먼저 읽을 것

### 3.1 기본값은 gl 입니다

`--viewer`를 생략하면 **네이티브 창이 뜹니다.** 아무 것도 안 보인다면 대개 `--viewer`를 잘못 준 것입니다.

### 3.2 뷰어 5종

| 옵션 | 무엇 | 언제 |
| --- | --- | --- |
| `gl` **(기본)** | 네이티브 OpenGL 창 | 그냥 볼 때. 기본이라 안 써도 됩니다 |
| `viser` | **브라우저** — `http://localhost:8080` | 창이 안 뜰 때, 원격, 다른 화면에서 볼 때 |
| `rerun` | Rerun 뷰어 | 시계열·로그와 함께 볼 때 |
| `usd` | **파일로 내보내기** | 외부 파이프라인으로 넘길 때. **화면에 안 보입니다** |
| `null` | 아무것도 안 그림 | CI, 벤치마크, "도는지만 확인" |

### 3.3 브라우저로 보기

```powershell
.\il.bat -p -m newton.examples cloth_hanging --viewer viser
```

실행하면 아래가 출력됩니다. 브라우저에서 그 주소를 엽니다.

```
+------ viser (listening *:8080) -------+
|   HTTP      | http://localhost:8080   |
|   Websocket | ws://localhost:8080     |
+---------------------------------------+
```

서버는 **예제가 도는 동안만** 살아 있습니다. 오래 보려면 `--num-frames`를 크게 주십시오.

### 3.4 안 보일 때 체크리스트

1. `--viewer null`이나 `--viewer usd`를 주지 않았는가 — 이 둘은 화면에 안 나옵니다
2. `--headless`를 주지 않았는가 — GL 뷰어를 헤드리스로 초기화합니다
3. `--num-frames`가 너무 작지 않은가 — 기본 100. 20~30이면 창이 뜨자마자 닫힙니다
4. 첫 실행이면 **커널 컴파일로 40초 이상 멈춰 있을 수 있습니다.** 죽은 게 아닙니다 (10절)
5. 그래도 창이 안 뜨면 `--viewer viser`로 브라우저에서 확인하십시오

---

## 4. 공통 인자 — 모든 예제

| 인자 | 기본값 | 설명 |
| --- | --- | --- |
| `--device DEVICE` | 자동 | Warp 디바이스. `cuda:0`, `cpu` |
| `--viewer {gl,usd,rerun,null,viser}` | `gl` | 3절 참조 |
| `--output-path PATH` | `output.usd` | `--viewer usd`일 때 필수 |
| `--num-frames N` | `100` | 총 프레임 수 |
| `--headless` / `--no-headless` | off | GL 뷰어만 해당 |
| `--test` / `--no-test` | off | 테스트 모드. 종료 상태를 검증합니다 |
| `--quiet` / `--no-quiet` | off | Warp 컴파일 로그 억제 |
| `--benchmark [SECONDS]` | off | 워밍업 후 FPS 측정 |
| `--realtime` | off | 벤치마크 모드에서 프로세스 우선순위 최대 |
| `--warp-config KEY=VALUE` | — | `warp.config` 속성 덮어쓰기. 반복 가능 (부록 B) |
| `--rerun-address ADDR` | — | 외부 Rerun 서버. 예: `rerun+http://127.0.0.1:9876/proxy` |

---

## 5. 예제별 고유 인자

### 5.1 cloth

| 예제 | 인자 | 기본값 |
| --- | --- | --- |
| `cloth_hanging` | `--solver {semi_implicit,style3d,xpbd,vbd}` | `vbd` |
| | `--width N` | `64` |
| | `--height N` | `32` |

다른 cloth 예제(`cloth_franka`, `cloth_h1`, `cloth_twist`, `cloth_bending`, `cloth_rollers`, `cloth_poker_cards`, `cloth_style3d`)는 **공통 인자만** 받습니다.

### 5.2 cable

| 예제 | 인자 | 기본값 | 뜻 |
| --- | --- | --- | --- |
| `cable_bundle_hysteresis` | `--segments N` | `40` | 케이블 세그먼트 수 |
| | `--no-dahl` | off | Dahl 마찰 비활성 — 순수 탄성으로 |
| | `--eps-max F` | `2.0` | 최대 소성 변형 [rad] |
| | `--tau F` | `0.1` | 기억 감쇠 길이 [rad] |

`cable_twist`, `cable_pile`, `cable_y_junction`은 공통 인자만 받습니다.

**cable에서 물성을 만질 수 있는 예제는 `cable_bundle_hysteresis` 하나입니다.** 파라미터 감각은 여기서 잡는 것이 효율적입니다.

### 5.3 다른 예제의 opt-in 인자

일부 예제만 추가로 받는 인자입니다.

| 인자 | 기본값 | 받는 예제 |
| --- | --- | --- |
| `--broad-phase {nxn,sap,explicit}` | `explicit` | `pyramid` |
| `--use-mujoco-contacts` | — | `ik_cube_stacking`, `robot_anymal_c_walk`, `robot_anymal_d`, `robot_g1`, `robot_h1` |

프레임워크에 헬퍼가 5개 있습니다 — `broad_phase`, `mujoco_contacts`, `kamino_contacts`, `world_count`, `max_worlds`. 직접 예제를 쓸 때 붙일 수 있습니다.

---

## 6. cable / cloth 예제 목록

### 6.1 cable — 4개

| 예제 | 내용 |
| --- | --- |
| `cable_twist` | 꼬임 |
| `cable_pile` | 무더기 쌓기 |
| `cable_bundle_hysteresis` | 번들 이력현상 (Dahl 마찰) |
| `cable_y_junction` | Y 분기 |

솔버는 `SolverVBD`입니다. 실행하면 XPBD 커널도 함께 올라옵니다.

### 6.2 cloth — 8개

| 예제 | 내용 |
| --- | --- |
| `cloth_hanging` | 매달림. **솔버 4개를 인자로 비교 가능** |
| `cloth_franka` | Franka가 cloth 조작 |
| `cloth_h1` | 휴머노이드 + cloth |
| `cloth_twist` | 꼬임 |
| `cloth_bending` | 굽힘 |
| `cloth_rollers` | 롤러 통과 |
| `cloth_poker_cards` | 카드 |
| `cloth_style3d` | Style3D 솔버 전용 |

### 6.3 솔버 8종

```
SolverVBD  SolverStyle3D  SolverXPBD  SolverMuJoCo
SolverFeatherstone  SolverImplicitMPM  SolverKamino  SolverSemiImplicit
```

- cloth → `SolverVBD` 또는 `SolverStyle3D`
- cable → `SolverVBD`
- Style3D는 `precompute()`에 약 2.9초가 추가로 듭니다. 벤치마크에서 이 비용을 분리하십시오

---

## 7. 레시피 — 복사해서 쓰는 것

### 7.1 그냥 보기

```powershell
.\il.bat -p -m newton.examples cable_twist
```

### 7.2 브라우저로 오래 보기

```powershell
.\il.bat -p -m newton.examples cloth_hanging --viewer viser --num-frames 2000 --quiet
```

### 7.3 도는지만 빠르게 확인

```powershell
.\il.bat -p -m newton.examples cable_twist --viewer null --num-frames 30 --quiet
```

### 7.4 해상도를 낮춰 가볍게

```powershell
.\il.bat -p -m newton.examples cloth_hanging --width 32 --height 16
```

### 7.5 솔버 비교 — FPS로

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver vbd --benchmark 10 --viewer null
```

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver style3d --benchmark 10 --viewer null
```

**벽시계 시간으로 비교하지 마십시오.** 짧은 실행은 대부분이 커널 컴파일과 초기화 비용입니다.

### 7.6 cable 물성 바꿔 보기

```powershell
.\il.bat -p -m newton.examples cable_bundle_hysteresis --segments 80 --eps-max 4.0
```

```powershell
.\il.bat -p -m newton.examples cable_bundle_hysteresis --no-dahl
```

### 7.7 USD로 내보내기

```powershell
.\il.bat -p -m newton.examples cloth_hanging --solver style3d --viewer usd --output-path out\cloth.usd --num-frames 60
```

---

## 8. USD 내보내기와 재생

### 8.1 나오는 것

`--viewer usd`는 **시간 샘플이 들어간 애니메이션 USD**를 씁니다. 정적 스냅샷이 아닙니다.

```
startTimeCode : 0.0
endTimeCode   : 20.0        (--num-frames 20 으로 실행한 경우)
FPS           : 60
defaultPrim   : /root

/root/model/triangles    Mesh     timeSamples 18   <- 변형되는 cloth
/root/model/particles    Points   timeSamples 18
/root/geometry/plane_0   Mesh     timeSamples 1    <- 정적
```

### 8.2 보는 방법이 별도로 필요합니다

USD는 **내보내기 포맷이고, Newton이 재생해 주지 않습니다.**

| 도구 | 이 머신 상태 |
| --- | --- |
| `usdview` | **없음.** pip `usd-core`에는 포함되지 않습니다 |
| Isaac Sim 6.0.1 | **있음** — `D:\isaac_601\isaac-sim.bat`. 첫 부팅 수 분 |
| Blender | 미확인 |

**반복 확인용으로 USD를 쓰지 마십시오.** 보려면 `--viewer gl` 또는 `viser`가 맞고, USD는 외부 파이프라인으로 넘길 때만 쓰십시오.

---

## 9. Newton 네이티브 기록·재생

USD를 거치지 않고 Newton 안에서 완결되는 경로입니다. 포맷은 `.bin`입니다.

### 9.1 기록

```python
viewer = newton.viewer.ViewerFile("my_recording.bin")
viewer.set_model(model)
viewer.log_state(state)   # 자동 기록
viewer.close()            # 자동 저장
```

참고 예제:

```powershell
.\il.bat -p -m newton.examples recording
```

### 9.2 재생

```powershell
.\il.bat -p -m newton.examples replay_viewer
```

ViewerGL 위에 재생 UI가 뜨고, 파일 다이얼로그로 `.bin`을 불러옵니다.

---

## 10. 성능과 컴파일 시간

### 10.1 첫 실행은 느립니다 — 정상입니다

Warp는 커널을 **아키텍처별로 컴파일**하고 캐시합니다. `cable_twist` 첫 실행 실측:

| 모듈 | 시간 |
| --- | --- |
| `xpbd/kernels` | 14.8초 |
| `vbd/rigid_vbd_kernels` | 9.0초 |
| `narrow_phase_gjk_mpr` | 8.9초 |
| 그 외 7개 | 9.6초 |
| **합계** | **42.3초** (10개 컴파일, 3개 캐시 히트) |

캐시 위치:

```
%LOCALAPPDATA%\NVIDIA\warp\Cache\1.13.0
```

**다른 GPU 아키텍처에서는 전부 다시 컴파일됩니다.** 실패가 아니라 첫 실행이 느린 것입니다. 판단 기준은 시간이 아니라 **컴파일 에러 유무**입니다.

### 10.2 컴파일 로그 숨기기

```
--quiet
```

### 10.3 속도 측정

```
--benchmark 10 --viewer null
```

워밍업 후 FPS를 잽니다. 뷰어를 끄고 재는 것이 맞습니다.

---

## 11. 함정

| 증상 | 원인 | 대응 |
| --- | --- | --- |
| 아무것도 안 보인다 | `--viewer null` / `usd` / `--headless` | 옵션을 빼거나 `--viewer viser` |
| `UnicodeEncodeError: 'cp949' ... in position 58xxxx` | **Warp 버그** — 생성한 `.cu` 소스를 인코딩 지정 없이 씁니다. kamino 솔버가 걸립니다 | `set PYTHONUTF8=1`. `il.bat`이 자동 설정합니다. `PYTHONIOENCODING`은 효과 없습니다 |
| 창이 떴다가 바로 닫힌다 | `--num-frames`가 작다 | 크게 주십시오 |
| 40초 이상 멈춘다 | 첫 실행 커널 컴파일 | 기다립니다. 두 번째부터 빠릅니다 |
| USD를 열 수 없다 | 뷰어가 없다 | Isaac Sim으로 열거나, USD 대신 `gl`/`viser` |
| 로그에 `_event_killfocus` Traceback | pyglet 창 포커스 콜백 | 무해. `Exception ignored`로 진행됩니다 |
| `invalid inertia tensor` 경고 | 예제 자산 자체의 경고 | 무해 |
| `Failed to get root com velocity` | 고정 articulation | 메시지가 정상이라고 말합니다 |

---

## 부록 A. 전체 예제 68개

**basic** `basic_conveyor` `basic_heightfield` `basic_joints` `basic_pendulum` `basic_plotting` `basic_shapes` `basic_urdf` `basic_viewer` `recording` `replay_viewer`

**cable** `cable_bundle_hysteresis` `cable_pile` `cable_twist` `cable_y_junction`

**cloth** `cloth_bending` `cloth_franka` `cloth_h1` `cloth_hanging` `cloth_poker_cards` `cloth_rollers` `cloth_style3d` `cloth_twist`

**contacts** `brick_stacking` `contacts_rj45_plug` `nut_bolt_hydro` `nut_bolt_sdf` `pyramid`

**diffsim** `diffsim_ball` `diffsim_bear` `diffsim_cloth` `diffsim_drone` `diffsim_soft_body` `diffsim_spring_cage`

**ik** `ik_cube_stacking` `ik_custom` `ik_franka` `ik_h1`

**kamino** `kamino_basic_dr_testmech` `kamino_basic_fourbar` `kamino_basic_heterogeneous` `kamino_robot_anymal_d` `kamino_robot_dr_legs`

**mpm** `mpm_anymal` `mpm_beam_twist` `mpm_grain_rendering` `mpm_granular` `mpm_multi_material` `mpm_snow_ball` `mpm_twoway_coupling` `mpm_viscous`

**multiphysics** `softbody_dropping_to_cloth` `softbody_gift`

**robot** `robot_allegro_hand` `robot_anymal_c_walk` `robot_anymal_d` `robot_cartpole` `robot_g1` `robot_h1` `robot_panda_hydro` `robot_policy` `robot_ur10`

**selection** `selection_articulations` `selection_cartpole` `selection_materials` `selection_multiple`

**sensor** `sensor_contact` `sensor_imu` `sensor_tiled_camera`

**softbody** `softbody_franka`

---

## 부록 B. --warp-config 주요 키

`--warp-config KEY=VALUE` 형태로 주고, 반복해서 여러 개를 줄 수 있습니다.

| 키 | 기본 | 용도 |
| --- | --- | --- |
| `enable_backward` | `True` | 미분이 필요 없으면 `False` — 컴파일 시간 감소 |
| `kernel_cache_dir` | `None` | 커널 캐시 위치 변경 |
| `cache_kernels` | `True` | `False`면 매번 재컴파일 (디버깅) |
| `load_module_max_workers` | `0` | 모듈 로드 병렬화 |
| `ptx_target_arch` | `None` | PTX 타깃 아키텍처 |
| `cuda_arch_suffix` | `None` | CUDA 아키텍처 접미사 |
| `mode` | `release` | `debug`로 전환 |
| `max_unroll` | `16` | 루프 언롤 한도 |
| `verbose` / `verbose_warnings` | `False` | 상세 로그 |
| `verify_cuda` | `False` | CUDA 호출 검증 |
| `print_launches` | `False` | 커널 런치 출력 |

예:

```powershell
.\il.bat -p -m newton.examples cable_twist --warp-config enable_backward=False --warp-config max_unroll=8
```

---

## 부록 C. 이 문서의 근거

| 항목 | 출처 |
| --- | --- |
| 공통 인자 | `newton/examples/__init__.py` argparse 및 `<example> --help` |
| 예제 고유 인자 | 각 예제 파일의 `add_argument` |
| 뷰어 기본값 `gl` | `newton/examples/__init__.py:459` |
| USD 시간 샘플 | 생성물을 `pxr.Usd`로 직접 검사 |
| 컴파일 시간 | `cable_twist` 첫 실행 로그 (RTX 4060, sm_89) |
| 솔버 목록 | `newton.solvers` 런타임 검사 |
| 예제 68개 | `python -m newton.examples --list` |
