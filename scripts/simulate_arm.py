import mujoco
import mujoco.viewer
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 加载新的模型文件
model = mujoco.MjModel.from_xml_path(str(ROOT / "models" / "arm.xml"))
data = mujoco.MjData(model)

print("正在启动机械臂肌腱仿真... 按 ESC 键或关闭窗口退出。")

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(0.01)