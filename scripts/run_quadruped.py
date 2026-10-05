"""
让四足机器人在 MuJoCo 里「跑起来」的最小示例。

它做的事：
  1. 加载 quadruped.xml
  2. 用一个「对角步态(trot)」正弦控制器，在每一步写 data.ctrl
  3. 推进仿真并可视化

用法：
  python run_quadruped.py                 # 开窗口看它走（需要图形界面）
  python run_quadruped.py --headless      # 不开窗口，跑 8 秒后打印结果（用来调参/验证）
  python run_quadruped.py --freq 2.4 --amp-thigh 0.45 --amp-knee 0.38

概念补充见同目录的《四足机器人仿真路线.md》
"""

import argparse
import time
from pathlib import Path

import numpy as np
import mujoco
import mujoco.viewer

ROOT = Path(__file__).resolve().parent.parent   # 仓库根目录


# ----------------------------------------------------------------------
# 步态控制器：对角步态 (trot)
# ----------------------------------------------------------------------
# 对角的两条腿同相：FL+RR 为一组，FR+RL 为另一组。
# 每组用一个正弦驱动大腿(pitch)，用余弦驱动小腿(knee)，相位刚好错开，
# 使得「支撑相腿向后蹬 → 摆动相抬腿前摆」，从而产生前进。
LEG_PHASE = {
    "FL": 0.0,
    "RR": 0.0,
    "FR": 0.5,
    "RL": 0.5,
}


def trot_control(data, model, t, freq, amp_thigh, amp_knee):
    """按当前时间 t 写入 data.ctrl。角度单位全部是【弧度】。"""
    omega = 2.0 * np.pi * freq

    for leg, phase in LEG_PHASE.items():
        theta = omega * t + 2.0 * np.pi * phase
        thigh = amp_thigh * np.sin(theta)              # 大腿前后摆
        knee = -amp_knee * np.sin(theta)               # 与大腿反相：支撑时伸、摆动时收

        # 用名字拿到执行器下标，比硬编码 0..7 更稳
        data.ctrl[model.actuator(f"{leg}_thigh_a").id] = thigh
        data.ctrl[model.actuator(f"{leg}_knee_a").id] = knee


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="MuJoCo 四足 trot 步态最小示例")
    parser.add_argument("--xml", default="models/quadruped.xml", help="模型文件(相对仓库根目录)")
    parser.add_argument("--headless", action="store_true", help="不开窗口，只跑物理")
    parser.add_argument("--seconds", type=float, default=8.0, help="仿真时长(秒)")
    parser.add_argument("--freq", type=float, default=2.4, help="步态频率(Hz)")
    parser.add_argument("--amp-thigh", type=float, default=0.45, help="大腿摆幅(rad)")
    parser.add_argument("--amp-knee", type=float, default=0.38, help="小腿摆幅(rad)")
    args = parser.parse_args()

    amp_thigh = args.amp_thigh
    amp_knee = args.amp_knee

    xml = Path(args.xml)
    if not xml.is_absolute():
        xml = ROOT / xml
    model = mujoco.MjModel.from_xml_path(str(xml))
    data = mujoco.MjData(model)

    print(f"模型: {xml}")
    print(f"  nq={model.nq} nv={model.nv} nu={model.nu}  (位置/速度/执行器维度)")
    print(f"  重力={model.opt.gravity}  timestep={model.opt.timestep}")

    root_id = model.body("root").id

    if args.headless:
        start_x = data.body("root").xpos[0]
        n = int(args.seconds / model.opt.timestep)
        heights = []
        for i in range(n):
            trot_control(data, model, data.time, args.freq, amp_thigh, amp_knee)
            mujoco.mj_step(model, data)
            if i % 50 == 0:
                heights.append(data.body("root").xpos[2])

        xpos = data.body("root").xpos
        travelled = xpos[0] - start_x
        print("\n--- 结果 ---")
        print(f"  前进距离 Δx = {travelled:+.3f} m")
        print(f"  最终躯干高度 z = {xpos[2]:.3f} m  (初始 0.28)")
        print(f"  平均躯干高度  = {np.mean(heights):.3f} m")
        print(f"  最终朝向四元数 = {data.body('root').xquat}")
        print(f"  是否还站着: {'是' if xpos[2] > 0.15 else '否（翻了）'}")
        return

    print("\n启动可视化…（鼠标左键拖拽=旋转视角，右键=平移，滚轮=缩放，ESC 退出）")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        viewer.cam.trackbodyid = root_id
        while viewer.is_running():
            step_start = time.time()
            trot_control(data, model, data.time, args.freq, amp_thigh, amp_knee)
            mujoco.mj_step(model, data)
            viewer.sync()
            # 按真实时间播放
            dt = model.opt.timestep - (time.time() - step_start)
            if dt > 0:
                time.sleep(dt)


if __name__ == "__main__":
    main()
