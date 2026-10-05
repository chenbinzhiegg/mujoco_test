import mujoco
import mujoco.viewer
import time

# 1. 加载模型
model = mujoco.MjModel.from_xml_path('hello.xml')
# 2. 创建数据容器（存储仿真状态）
data = mujoco.MjData(model)

print("正在启动仿真... 按 ESC 键或关闭窗口退出。")

# 3. 启动被动可视化查看器 (Passive Viewer)
with mujoco.viewer.launch_passive(model, data) as viewer:
    # 4. 仿真主循环
    while viewer.is_running():
        mujoco.mj_step(model, data) # 推进物理仿真一步
        viewer.sync()               # 将物理状态同步到渲染画面
        time.sleep(0.01)            # 暂停 10ms，让画面看起来像正常速度播放

print("仿真结束。")
