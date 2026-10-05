# MuJoCo 学习仓库

用 [MuJoCo](https://mujoco.readthedocs.io/en/stable/overview.html) 学习机器人仿真的实验仓库：
从最小的「会掉下来的盒子」，到机械臂，再到**四足机器人走起来**。

---

## 从哪开始？（推荐阅读顺序）

| 顺序 | 文档 | 内容 |
|------|------|------|
| 1️⃣ | [`docs/01-MuJoCo快速上手.md`](docs/01-MuJoCo快速上手.md) | **先读这个**。MuJoCo 怎么运行、XML 文件怎么看、怎么仿真、怎么操控 |
| 2️⃣ | [`docs/02-四足机器人仿真路线.md`](docs/02-四足机器人仿真路线.md) | 进阶：浮基、执行器、步态、强化学习路线图 |
| 3️⃣ | [`docs/03-Go2使用与改动说明.md`](docs/03-Go2使用与改动说明.md) | Go2 模型从哪来、有没有被改过、控制脚本做了什么 |
| 🔧 | [`docs/04-Git推送与网络排查.md`](docs/04-Git推送与网络排查.md) | **工具篇**：`git push` 卡住怎么查（跟 MuJoCo 无关，但迟早用得上） |

看不懂代码没关系：**先按顺序读文档、把例子跑起来看一眼**，比死磕代码有效。

---

## 环境要求

- Python + `mujoco`（本仓库用 conda 环境 `mujoco_env`，mujoco 3.14.0）
- 想开窗口看仿真需要图形界面；没有图形界面就用 `--headless` 看数值结果

```bash
# 本机使用的 Python 解释器
/home/egg/miniconda3/envs/mujoco_env/bin/python
```

---

## 快速开始

```bash
cd /home/egg/Projects/mujoco_test

# 1) 最小例子：一个盒子自由落体，开窗口看
python scripts/simulate.py

# 2) 机械臂 + 肌腱
python scripts/simulate_arm.py

# 3) 四足（自造极简模型）走起来
python scripts/run_quadruped.py              # 开窗口
python scripts/run_quadruped.py --headless   # 不开窗口，打印前进距离

# 4) 真机 Unitree Go2：站立 / 行走
python scripts/run_go2.py --mode hold        # 站住
python scripts/run_go2.py --mode trot        # 走起来
python scripts/run_go2.py --mode trot --headless
```

> 所有脚本都可以**从任意目录运行**（脚本会自己定位模型文件，不用先 `cd`）。

**开窗口后的操作**：鼠标左键拖拽=旋转视角，右键=平移，滚轮=缩放，`ESC` 退出。

---

## 目录结构

```
mujoco_test/
├── README.md                    本文件
├── models/                      所有 MJCF 模型（XML）
│   ├── hello.xml                最小模型：一个自由落体的盒子
│   ├── arm.xml                  7 自由度机械臂 + 空间肌腱（无执行器）
│   ├── quadruped.xml            自造极简四足（躯干 + 4 腿 × 2 关节 = 8 执行器）
│   └── unitree_go2/             Unitree Go2 真机模型（从 Menagerie 复制，未改动）
├── scripts/                     Python 仿真脚本
│   ├── simulate.py              跑 hello.xml（最小仿真流程）
│   ├── simulate_arm.py          跑 arm.xml
│   ├── run_quadruped.py         四足步态控制（位置执行器）
│   └── run_go2.py               Go2 控制（力矩电机 + PD）
└── docs/                        中文教程
    ├── 01-MuJoCo快速上手.md
    ├── 02-四足机器人仿真路线.md
    ├── 03-Go2使用与改动说明.md
    └── 04-Git推送与网络排查.md
```

---

## 脚本速查

| 脚本 | 模型 | 控制方式 | 说明 |
|------|------|----------|------|
| `scripts/simulate.py` | `hello.xml` | 无（被动） | 最小仿真循环，读懂它就懂 MuJoCo 的骨架 |
| `scripts/simulate_arm.py` | `arm.xml` | 无（被动） | 看复杂模型怎么组织 |
| `scripts/run_quadruped.py` | `quadruped.xml` | **位置伺服**（`ctrl`=目标角度） | 对角步态，8 秒约走 5 m |
| `scripts/run_go2.py` | `unitree_go2/scene.xml` | **力矩电机**（`ctrl`=力矩） | 自己写 PD；5 秒约走 2.4 m |

---

## 模型说明

| 模型 | 来源 | 是否修改 |
|------|------|----------|
| `hello.xml` / `arm.xml` / `quadruped.xml` | 本仓库自己写的 | — |
| `unitree_go2/` | [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) 官方 | **未改动**（BSD-3-Clause） |

> 从 Menagerie 复制来的模型**保持原样**。要改就在副本上改，别动源文件。
> 详见 [`docs/03-Go2使用与改动说明.md`](docs/03-Go2使用与改动说明.md)。

---

## 参考链接

- MuJoCo 官方文档：<https://mujoco.readthedocs.io/en/stable/overview.html>
- MuJoCo XML 参考：<https://mujoco.readthedocs.io/en/stable/XMLreference.html>
- Python 用法：<https://mujoco.readthedocs.io/en/stable/python.html>
- 现成高质量模型（Menagerie）：<https://github.com/google-deepmind/mujoco_menagerie>
- 四足强化学习（MuJoCo Playground）：<https://github.com/google-deepmind/mujoco_playground>
