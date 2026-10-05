"""
Unitree Go2 四足仿真：加载本地 Menagerie 模型 + PD 关节力矩控制。

Go2 用的是【力矩电机】(motor)，所以控制流程是：
    tau = kp * (q_target - q) - kd * qd      # 自己算 PD
    data.ctrl[:] = tau                       # ctrl 的单位是 N·m（力矩）

用法：
    python run_go2.py --mode hold            # 站住（PD 保持 home 姿态）
    python run_go2.py --mode trot            # 对角步态，尝试走动
    python run_go2.py --mode hold --headless # 无窗口 + 打印结果

注意：模型是从 Menagerie 复制到本工作区的副本（unitree_go2/），源文件未改动。
"""

import argparse
import time
from pathlib import Path

import numpy as np
import mujoco
import mujoco.viewer

ROOT = Path(__file__).resolve().parent.parent   # 仓库根目录


def build_pd_targets(q_home, mode, t, freq, amp_thigh, amp_calf):
    """返回 12 维目标关节角（弧度）。

    hold: 直接用 home 关键帧的关节角。
    trot: 在 home 基础上叠加对角步态正弦（FL+RR 同相，FR+RL 反相）。
    """
    target = q_home.copy()

    if mode == "trot":
        omega = 2.0 * np.pi * freq
        # 执行器顺序：FL_hip, FL_thigh, FL_calf, FR_*, RL_*, RR_*（每腿 3 个）
        leg_phase = [0.0, np.pi, np.pi, 0.0]   # FL, FR, RL, RR
        for leg in range(4):
            theta = omega * t + leg_phase[leg]
            i = 3 * leg
            target[i + 1] += amp_thigh * np.sin(theta)      # thigh
            target[i + 2] += amp_calf * np.sin(theta + np.pi / 2)  # calf

    return target


def main():
    parser = argparse.ArgumentParser(description="Go2 力矩控制最小示例")
    parser.add_argument("--xml", default="models/unitree_go2/scene.xml")
    parser.add_argument("--mode", choices=["hold", "trot"], default="hold")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument("--kp", type=float, default=40.0, help="关节位置增益")
    parser.add_argument("--kd", type=float, default=1.0, help="关节速度阻尼")
    parser.add_argument("--freq", type=float, default=2.4, help="步态频率 Hz（调参结果）")
    parser.add_argument("--amp-thigh", type=float, default=0.55, help="大腿摆幅(rad)（调参结果）")
    parser.add_argument("--amp-calf", type=float, default=0.60, help="小腿摆幅(rad)（调参结果）")
    args = parser.parse_args()

    xml = Path(args.xml)
    if not xml.is_absolute():
        xml = ROOT / xml
    model = mujoco.MjModel.from_xml_path(str(xml))
    data = mujoco.MjData(model)

    key_id = model.key("home").id if model.nkey else 0
    if model.nkey:
        mujoco.mj_resetDataKeyframe(model, data, key_id)
    q_home = data.qpos[7:].copy()   # home 姿态的 12 个腿部关节角，作为 PD 目标基准

    print(f"模型: {args.xml}")
    print(f"  nq={model.nq} nv={model.nv} nu={model.nu}  nkey={model.nkey}")
    print(f"  关节名: {[model.joint(i).name for i in range(1, model.njnt)]}")
    print(f"  执行器: {[model.actuator(i).name for i in range(model.nu)]}")
    print(f"  mode={args.mode}  kp={args.kp} kd={args.kd}")

    root_id = model.body("base").id

    if args.headless:
        n = int(args.seconds / model.opt.timestep)
        hs, xs = [], []
        for _ in range(n):
            target = build_pd_targets(q_home, args.mode,
                                      data.time, args.freq, args.amp_thigh, args.amp_calf)
            q = data.qpos[7:]
            qd = data.qvel[6:]
            data.ctrl[:] = args.kp * (target - q) - args.kd * qd
            mujoco.mj_step(model, data)
            hs.append(data.qpos[2])
            xs.append(data.qpos[0])

        print("\n--- 结果 ---")
        print(f"  前进距离 Δx      = {xs[-1] - xs[0]:+.3f} m")
        print(f"  最终/平均躯干高度 = {hs[-1]:.3f} / {np.mean(hs):.3f} m  (home 为 0.27)")
        print(f"  是否还站着: {'是' if hs[-1] > 0.18 else '否（翻了/塌了）'}")
        return

    print("\n启动可视化…（ESC 退出）")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        viewer.cam.trackbodyid = root_id
        while viewer.is_running():
            step_start = time.time()
            target = build_pd_targets(q_home, args.mode,
                                      data.time, args.freq, args.amp_thigh, args.amp_calf)
            q = data.qpos[7:]
            qd = data.qvel[6:]
            data.ctrl[:] = args.kp * (target - q) - args.kd * qd
            mujoco.mj_step(model, data)
            viewer.sync()
            dt = model.opt.timestep - (time.time() - step_start)
            if dt > 0:
                time.sleep(dt)


if __name__ == "__main__":
    main()
