# WMQ

# TYY

## SSUP Simulator

所有ssup_simulator文件夹下的文件请移放至tool-games/environment文件夹下运行

Simulator采用简单的CNN网络，输入是一张(128, 128, 3)的RGB图片，输出是单通道的预测的Reward Value

**ssup_simulator.py文件中存放了模型结构。**

**ssup_simulator_dataset.py文件中存放了数据集结构。**

**train.py提供了训练代码**

**test.py提供了测试代码**
test.py中选择开启top_k即可视化出随机采样点中Reward Value预测最高的k个点，不开启则可视化出所有的采样点。
采样点可视化颜色由Reward Value决定。Reward Value越低，颜色越偏红；Reward Value越高，颜色越偏绿。
可以在vis_result文件夹中查看到已有的可视化结果。

**reward_function.py提供了计算Ground Truth Reward Value的方法**

**以场景名称命名的.py文件执行随机生成场景的任务**
*bridge.py*
*catapult.py*

# WLH

# GKZ

# GCY
