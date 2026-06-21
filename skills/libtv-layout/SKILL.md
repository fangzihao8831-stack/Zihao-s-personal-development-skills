---
name: libtv-layout
description: Use when creating multiple LibTV canvas nodes, automatic LibTV/Seedance video-generation nodes,素材节点,分组, or any LibTV CLI workflow that must keep nodes tidy, left-to-right, non-overlapping, and correctly connected with {{Mixed N}} input order.
---

# LibTV Layout

## 目标

创建 LibTV 节点时，先排版再创建。不要先乱堆节点再整理。

这个 skill 用于：

- 自动生成 LibTV 视频节点、素材节点、分组。
- 批量创建短剧分镜、Seedance 视频节点、角色/场景/道具/音频参考。
- 需要画布整齐、分组不重叠、连线和 prompt 顺序正确的任务。

## 默认布局

默认使用左到右生产线：

- 左侧：素材区，放角色、场景、道具、音频、参考视频和额外输入素材。
- 中间：正式视频时间线，按 `V01 -> V02 -> V03` 从左到右。
- 下方：`TEST`、`OLD`、失败版、备选版、参考节点。
- 右侧：输出、合成、最终成片或交付节点。没有输出节点时不要硬建。

多个集数、场景、角色组或任务类别要分成独立分组/泳道。分组之间必须留空，不能重叠。

## LibTV 标签规则

本工作区默认按当前视频节点的真实输入顺序写 `{{Mixed N}}`。

- 第 1 个连接到视频节点的输入素材 = `{{Mixed 1}}`
- 第 2 个连接到视频节点的输入素材 = `{{Mixed 2}}`
- 第 3 个连接到视频节点的输入素材 = `{{Mixed 3}}`

图片、音频、视频、混合素材都走同一条 `Mixed` 顺序；不要默认按文件类型写 `{{Image 1}}`、`{{Audio 1}}`。只有用户明确说 UI 显示了这些标签时才使用。

写 prompt 时必须在 `Continuity Notes` 或等价段落说明每个 `{{Mixed N}}` 的用途。创建后必须回读节点，检查输入顺序与 prompt 说明一致。

## 执行流程

1. 先做 dry-run，简短列出会创建几个素材、正式视频、参考节点、输出节点和分组。
2. 用户确认后再创建。
3. 先创建所有输入素材，再创建视频节点。
4. 如果素材已经有本地文件路径，在计划里写 `resource` 或 `file`，脚本会用 LibTV CLI 上传成真实图片/音频/视频素材节点。
5. 没有本地文件路径时，才创建占位素材节点或 LibTV 画布节点；最终交付时要说明这些素材还没有真实生成或上传。
6. 创建视频节点时用真实输入素材连线，不要只在 prompt 里假装引用。
7. 创建分组，把节点绑定到对应分组。
8. 回读目标画布并验证。

复杂任务优先使用脚本：

```text
scripts/libtv-layout-create.mjs
```

计划文件里的素材节点可以这样写真实文件：

```json
{
  "key": "char_lina",
  "type": "image",
  "name": "角色_Lina_身份锁定图",
  "resource": "C:/path/to/lina.png"
}
```

## 验证要求

完成后必须回读目标画布，检查：

- 分组之间没有重叠。
- 分组内部节点没有明显重叠。
- 正式视频节点从左到右排列。
- 每个视频节点都有真实输入连线。
- `{{Mixed N}}` 顺序和输入素材顺序一致。
- prompt 已写入。
- 重名素材已经按用途重命名，避免误连。

## 失败处理

- 不要自动创建多个测试画布。
- 优先修复同一个目标画布。
- 如果必须新建画布，先说明原因。
- 最终只把有效画布作为结果交付，并说明验证结果。
