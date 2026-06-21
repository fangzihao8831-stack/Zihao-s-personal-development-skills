#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);

function argValue(name) {
  const i = args.indexOf(name);
  if (i === -1) return undefined;
  return args[i + 1];
}

const execute = args.includes("--execute");
const dryRun = args.includes("--dry-run") || !execute;
const demo = args.includes("--demo");
const planPath = argValue("--plan");
const projectNameOverride = argValue("--project-name");
const projectIdOverride = argValue("--project-id");
const verifyProjectId = argValue("--verify-project");

const cwd = process.cwd();
const libtv = process.env.LIBTV_CLI || path.join(cwd, "libtv-cli", "bin", "libtv.exe");

function run(argsList) {
  return execFileSync(libtv, argsList, {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    maxBuffer: 100 * 1024 * 1024,
  });
}

function runJson(argsList) {
  return JSON.parse(run(argsList));
}

function jsonValue(value) {
  return JSON.stringify(value);
}

function uniqueByName(items) {
  const seen = new Map();
  return items.map((item) => {
    const base = item.name || item.key;
    const count = seen.get(base) || 0;
    seen.set(base, count + 1);
    if (count === 0) return item;
    return { ...item, name: `${base}_${item.key}` };
  });
}

function demoPlan() {
  return {
    projectName: projectNameOverride || "LibTV Layout Skill Demo",
    description: "Demo canvas created by libtv-layout skill: left assets, middle timeline, lower references, right output.",
    groups: {
      assets: "01_ASSETS_left_source_pool",
      videos: "02_ACTIVE_TIMELINE_middle",
      references: "03_REFERENCE_TEST_lower_lane",
      outputs: "04_OUTPUT_right",
    },
    assets: [
      {
        key: "char_lina",
        type: "image",
        name: "角色_Lina_身份锁定图",
        params: {
          prompt: "成年女性 Lina，夜班护士，深色短发，浅蓝制服，疲惫但坚定，角色设定三视图，写实短剧风格。",
          model: "Lib Image",
          count: 1,
          settings: { quality: "medium", resolution: "2K", ratio: "16:9" },
          modeType: "text2image",
        },
      },
      {
        key: "scene_corridor",
        type: "image",
        name: "场景_医院夜间走廊",
        params: {
          prompt: "深夜医院走廊，冷白荧光灯，地面反光，远处护士站半暗，写实短剧场景参考图。",
          model: "Lib Image",
          count: 1,
          settings: { quality: "medium", resolution: "2K", ratio: "16:9" },
          modeType: "text2image",
        },
      },
      {
        key: "prop_folder",
        type: "image",
        name: "道具_封口病历袋",
        params: {
          prompt: "一个牛皮纸封口病历袋，边角磨损，红色封条，不要可读文字，干净产品参考图。",
          model: "Lib Image",
          count: 1,
          settings: { quality: "medium", resolution: "2K", ratio: "16:9" },
          modeType: "text2image",
        },
      },
    ],
    videos: [
      {
        key: "v01",
        type: "video",
        name: "V01 00:00-00:06 Lina发现病历袋",
        inputs: ["scene_corridor", "char_lina", "prop_folder"],
        prompt: [
          "# V01 00:00-00:06 Lina发现病历袋",
          "",
          "Timecode: 00:00-00:06",
          "Purpose: 建立深夜医院走廊和 Lina 发现异常病历袋的悬念。",
          "",
          "## Seedance 2.0 Prompt",
          "",
          "Shot 1: 使用 {{Mixed 1}} 作为医院夜间走廊场景参考，保持冷白荧光灯、反光地面和远处护士站。使用 {{Mixed 2}} 作为 Lina 人物身份参考，保持脸部、发型、制服和疲惫但坚定的状态。Lina 从画面左侧慢慢走入中景，脚步放轻，听见远处电梯提示音后停住。",
          "",
          "Shot 2: 使用 {{Mixed 3}} 作为封口病历袋道具参考。镜头切到地面低角度特写，病历袋半露在护士站桌下，红色封条清楚但不要生成可读文字。Lina 的手伸入画面，停在病历袋上方，没有立刻拿起。",
          "",
          "Dialogue:",
          "\"这是谁留下的？\"",
          "",
          "Sound: 深夜医院空调低频、远处电梯提示音、轻微脚步声，Lina 低声自语，声音清楚，无背景音乐。",
          "",
          "Continuity Notes: {{Mixed 1}} = 医院夜间走廊；{{Mixed 2}} = Lina 人物身份；{{Mixed 3}} = 封口病历袋道具。",
          "",
          "Constraints: 不要字幕；不要水印；不要Logo；不要可读文字；不要新增人物；不要改变 Lina 的脸、发型和制服；不要夸张表演。",
        ].join("\n"),
        params: {
          model: "Seedance 2.0 Fast VIP",
          modeType: "mixed2video",
          count: 1,
          settings: { ratio: "16:9", resolution: "720p", duration: 6, enableSound: "on" },
          advancedSettings: { search_enabled: 1, autoCompliance: 1 },
        },
      },
      {
        key: "v02",
        type: "video",
        name: "V02 00:06-00:12 走廊灯光突然熄灭",
        inputs: ["scene_corridor", "char_lina", "prop_folder"],
        prompt: [
          "# V02 00:06-00:12 走廊灯光突然熄灭",
          "",
          "Timecode: 00:06-00:12",
          "Purpose: 把悬念升级为危险感。",
          "",
          "## Seedance 2.0 Prompt",
          "",
          "Shot 1: 使用 {{Mixed 1}} 作为同一条医院夜间走廊场景参考，保持空间连续。使用 {{Mixed 2}} 作为 Lina 人物身份参考。Lina 把 {{Mixed 3}} 的封口病历袋拿到胸前，刚准备打开，走廊灯光闪烁两次。",
          "",
          "Shot 2: 灯光突然熄灭一半，Lina 抬头看向走廊尽头，身体僵住，呼吸变浅。镜头保持中近景，不要快速摇晃。",
          "",
          "Dialogue:",
          "\"有人吗？\"",
          "",
          "Sound: 荧光灯电流声、远处金属门轻响、Lina 压低声音发问，无背景音乐。",
          "",
          "Continuity Notes: {{Mixed 1}} = 同一医院走廊；{{Mixed 2}} = Lina 人物身份；{{Mixed 3}} = 封口病历袋道具。",
          "",
          "Constraints: 不要字幕；不要水印；不要Logo；不要可读文字；不要新增人物；不要改变 Lina 的脸；不要夸张恐怖效果。",
        ].join("\n"),
        params: {
          model: "Seedance 2.0 Fast VIP",
          modeType: "mixed2video",
          count: 1,
          settings: { ratio: "16:9", resolution: "720p", duration: 6, enableSound: "on" },
          advancedSettings: { search_enabled: 1, autoCompliance: 1 },
        },
      },
    ],
    references: [
      {
        key: "test_alt",
        type: "video",
        name: "TEST 走廊惊吓备选版",
        inputs: ["scene_corridor", "char_lina"],
        prompt: [
          "# TEST 走廊惊吓备选版",
          "",
          "Purpose: 仅作为备选参考，不作为正式时间线。",
          "",
          "使用 {{Mixed 1}} 作为同一医院夜间走廊场景参考，保持冷白灯光和压抑走廊空间。使用 {{Mixed 2}} 作为 Lina 人物身份参考，保持脸部、短发、护士制服和克制紧张状态。Lina 听见身后脚步但不回头，只让肩膀轻微绷紧。",
          "",
          "Continuity Notes: {{Mixed 1}} = 医院夜间走廊；{{Mixed 2}} = Lina 人物身份。",
          "",
          "Constraints: 仅作测试备选；不要字幕；不要水印；不要新增人物；不要改变 Lina 的脸。",
        ].join("\n"),
        params: {
          model: "Seedance 2.0 Fast VIP",
          modeType: "mixed2video",
          count: 1,
          settings: { ratio: "16:9", resolution: "480p", duration: 5, enableSound: "on" },
        },
      },
    ],
    outputs: [
      {
        key: "output_note",
        type: "text",
        name: "OUTPUT_交付说明",
        data: {
          content: ["正式时间线使用 V01 -> V02；TEST 节点仅作为备选参考。"],
          contentWidth: 350,
          contentHeight: 200,
        },
      },
    ],
  };
}

function loadPlan() {
  if (demo) return demoPlan();
  if (!planPath) throw new Error("需要 --plan <file>，或使用 --demo");
  return JSON.parse(fs.readFileSync(planPath, "utf8"));
}

function plannedLayout(plan) {
  const assets = uniqueByName(plan.assets ?? []);
  const videos = uniqueByName(plan.videos ?? []);
  const references = uniqueByName(plan.references ?? []);
  const outputs = uniqueByName(plan.outputs ?? []);

  const layout = [];
  assets.forEach((node, i) => layout.push({ lane: "assets", ...node, x: 40 + (i % 2) * 760, y: 80 + Math.floor(i / 2) * 430 }));
  videos.forEach((node, i) => layout.push({ lane: "videos", ...node, x: 1800 + i * 720, y: 80 }));
  references.forEach((node, i) => layout.push({ lane: "references", ...node, x: 1800 + i * 720, y: 650 }));
  outputs.forEach((node, i) => layout.push({ lane: "outputs", ...node, x: 1800 + Math.max(videos.length, 1) * 720 + 900, y: 80 + i * 430 }));
  return layout;
}

function projectCreate(plan) {
  if (projectIdOverride) return { projectUuid: projectIdOverride };
  const created = runJson(["project", "create", projectNameOverride || plan.projectName || "LibTV Layout Project", "-d", plan.description || "Created by libtv-layout skill."]);
  return { projectUuid: created.projectMeta.uuid };
}

function createNode(projectId, item, idMap) {
  if (item.resource || item.file) return uploadNode(projectId, item, idMap);

  const args = ["node", "--x", String(item.x), "--y", String(item.y), "create", item.name, "-p", projectId, "-t", item.type];
  for (const [key, value] of Object.entries(item.data ?? {})) args.push("-u", `${key}=${jsonValue(value)}`);
  for (const [key, value] of Object.entries(item.params ?? {})) {
    if (key === "prompt") continue;
    args.push("-s", `${key}=${jsonValue(value)}`);
  }
  for (const inputKey of item.inputs ?? []) {
    const inputId = idMap.get(inputKey);
    if (!inputId) throw new Error(`节点 ${item.key} 缺少输入素材: ${inputKey}`);
    args.push("--left-add", inputId);
  }
  if (item.prompt && item.type !== "video") args.push("--prompt", item.prompt);
  const created = runJson(args);
  const nodeId = created.nodeKey ?? created.id ?? findNodeByName(projectId, item.name)?.id;
  if (!nodeId) throw new Error(`无法确定节点 ID: ${item.name}`);
  if (item.prompt && item.type === "video") runJson(["node", nodeId, "-p", projectId, "--prompt", item.prompt]);
  idMap.set(item.key, nodeId);
  return { ...item, id: nodeId };
}

function uploadNode(projectId, item, idMap) {
  const rawFile = item.resource || item.file;
  const filePath = path.isAbsolute(rawFile) ? rawFile : path.resolve(cwd, rawFile);
  const args = ["upload", item.name, "-p", projectId, "-f", filePath, "--x", String(item.x), "--y", String(item.y)];
  const mediaType = item.mediaType || (["image", "video", "audio"].includes(item.type) ? item.type : undefined);
  if (mediaType) args.push("-t", mediaType);
  const created = runJson(args);
  const nodeId = created.nodeKey ?? created.id ?? findNodeByName(projectId, item.name)?.id;
  if (!nodeId) throw new Error(`无法确定上传素材节点 ID: ${item.name}`);
  idMap.set(item.key, nodeId);
  return { ...item, id: nodeId, uploadedFrom: filePath };
}

function findNodeByName(projectId, name) {
  return (runJson(["node", "list", "-p", projectId]).nodes ?? []).find((node) => node.name === name);
}

function createGroups(projectId, plan, createdItems) {
  const groupNames = {
    assets: plan.groups?.assets || "01_ASSETS_left_source_pool",
    videos: plan.groups?.videos || "02_ACTIVE_TIMELINE_middle",
    references: plan.groups?.references || "03_REFERENCE_TEST_lower_lane",
    outputs: plan.groups?.outputs || "04_OUTPUT_right",
  };
  const groups = [];
  for (const lane of ["assets", "videos", "references", "outputs"]) {
    const ids = createdItems.filter((item) => item.lane === lane).map((item) => item.id);
    if (ids.length === 0) continue;
    const argsList = ["group", "create", groupNames[lane], "-p", projectId];
    for (const id of ids) argsList.push("--node", id);
    const group = runJson(argsList);
    groups.push({ lane, name: groupNames[lane], id: group.groupNodeKey, childCount: ids.length });
  }
  return groups;
}

function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function verify(projectId) {
  const project = runJson(["project", projectId]);
  const nodes = project.nodes ?? [];
  const edges = project.edges ?? [];
  const groups = nodes
    .filter((node) => node.type === "group")
    .map((node) => ({ name: node.name, id: node.id, x: node.position?.x ?? 0, y: node.position?.y ?? 0, w: node.width ?? 0, h: node.height ?? 0, childCount: nodes.filter((child) => child.parentId === node.id).length }));
  const overlaps = [];
  for (let i = 0; i < groups.length; i += 1) {
    for (let j = i + 1; j < groups.length; j += 1) {
      if (rectsOverlap(groups[i], groups[j])) overlaps.push([groups[i].name, groups[j].name]);
    }
  }
  const videos = nodes
    .filter((node) => node.type === "video")
    .map((node) => {
      let detail = {};
      try {
        detail = runJson(["node", node.id, "-p", projectId]);
      } catch {}
      const params = detail.data?.params ?? {};
      const orderedInputs = [
        ...(params.mixedList ?? []),
        ...(params.imageList ?? []),
        ...(params.videoList ?? []),
        ...(params.audioList ?? []),
        ...(params.textList ?? []),
      ];
      const prompt = params.prompt ?? "";
      const expectedMixedTags = orderedInputs.map((_, index) => `{{Mixed ${index + 1}}}`);
      const missingMixedTags = expectedMixedTags.filter((tag) => !prompt.includes(tag));
      return {
        name: node.name,
        id: node.id,
        parent: groups.find((group) => group.id === node.parentId)?.name || "",
        x: node.position?.x ?? 0,
        y: node.position?.y ?? 0,
        incoming: edges.filter((edge) => edge.target === node.id).length,
        inputListCount: orderedInputs.length,
        hasPrompt: Boolean(params.prompt),
        expectedMixedTags,
        missingMixedTags,
      };
    });
  return { projectId, nodeCount: nodes.length, edgeCount: edges.length, groupCount: groups.length, overlapCount: overlaps.length, overlaps, groups, videos };
}

if (verifyProjectId) {
  console.log(JSON.stringify({ mode: "verify", verification: verify(verifyProjectId) }, null, 2));
  process.exit(0);
}

const plan = loadPlan();
const layout = plannedLayout(plan);

if (dryRun) {
  console.log(JSON.stringify({
    mode: "dry-run",
    projectName: projectNameOverride || plan.projectName,
    counts: {
      assets: layout.filter((item) => item.lane === "assets").length,
      videos: layout.filter((item) => item.lane === "videos").length,
      references: layout.filter((item) => item.lane === "references").length,
      outputs: layout.filter((item) => item.lane === "outputs").length,
    },
    layout: layout.map(({ key, name, type, lane, x, y, inputs }) => ({ key, name, type, lane, x, y, inputs: inputs ?? [] })),
  }, null, 2));
  process.exit(0);
}

const { projectUuid } = projectCreate(plan);
const idMap = new Map();
const createdItems = [];

for (const lane of ["assets", "videos", "references", "outputs"]) {
  for (const item of layout.filter((entry) => entry.lane === lane)) {
    createdItems.push(createNode(projectUuid, item, idMap));
  }
}

const groups = createGroups(projectUuid, plan, createdItems);
const report = verify(projectUuid);

console.log(JSON.stringify({
  mode: "execute",
  projectId: projectUuid,
  url: `https://www.liblib.tv/canvas?spaceId=732820&projectId=${projectUuid}`,
  groups,
  verification: report,
}, null, 2));
