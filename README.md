# World of Block · WOB

一个浏览器多人方块 RPG 的起点。首个可玩的场景是原创灰盒副本「余烬龙巢」。场地约 64 × 48 格，中央净高 32 格。沿着火柱走向龙台，可以观察烬翼从吸气预警到正面吐息的节奏。

## 本地运行

需要 Node.js 22.12+、npm、Rust stable 和 Protocol Buffers 编译器 `protoc`。首次编译 Rust 依赖需要几分钟。本机已经备有项目专用的 protoc。

```sh
git submodule update --init
npm ci
npm run server
```

保持服务端运行，在项目根目录打开第二个终端：

```sh
npm run dev
```

打开 <http://127.0.0.1:5180/>。两个标签页可加入同一场景。点击「进入巢穴」，WASD 移动、鼠标环视、空格跳跃、Esc 释放鼠标。浏览器限制指针锁定时，按住鼠标拖动环视。

## 项目结构

| 目录 | 用途 |
| --- | --- |
| `server/` | Rust 游戏服务。组装 Voxelize 世界，生成可行走的地面、穹顶、龙台和火柱。 |
| `client/` | 浏览器客户端。处理输入、其他玩家的显示，以及按服务器世界时间播放的吐息演示。 |
| [tools/generate_cinderwing.py](tools/generate_cinderwing.py) | 用 Python 生成烬翼的几何、材质、分组和站姿。 |
| `assets/cinderwing.bbmodel` | 可在 Blockbench 中编辑的烬翼模型原稿。 |
| `client/public/models/` | 游戏加载的 glTF 模型。更新模型时保留 Body、Head、Jaw、LeftWing、RightWing 分组，用米制比例导出并检查贴图路径。 |
| `engine/voxelize/` | 官方 Voxelize v3.0.0 引擎子模块。服务端从此编译，客户端使用匹配的 npm 发行包。 |

首版用于观察尺寸、绕行和多人同步。吐息采用固定的 12 秒周期，目前仅展示预警和动作。命中、生命值和胜负判定留待设计战斗时实现。

## 重新生成烬翼

在项目根目录运行 `python3 tools/generate_cinderwing.py`。脚本仅使用 Python 标准库，会重写 `assets/cinderwing.bbmodel` 和 `client/public/models/cinderwing.gltf`。如果在 Blockbench 里手调了模型，重新生成前请先保存改动的副本。

## 验证

```sh
sh server/run.sh test
npm run build
```

服务端默认监听本机 4100 端口，网页开发服务监听 5180 端口。更新引擎时，同步检查子模块提交、客户端 npm 版本和两个锁文件，再复测双人进入场景。
