# HTTP / Agent 接口

服务地址：`http://127.0.0.1:8777`。默认只监听 localhost，没有鉴权；不要把端口直接暴露到公网。

## 最小 Agent 调用

```bash
curl -X POST http://127.0.0.1:8777/api/run \
  -H "Content-Type: application/json" \
  -d '{"commands":"//pos1 0,0,0\n//pos2 3,3,3\n//set minecraft:glass","actor":"agent"}'
```

PowerShell：

```powershell
$body = @{
  commands = "//pos1 0,0,0`n//pos2 3,3,3`n//set minecraft:glass"
  actor = "agent"
} | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8777/api/run" -ContentType "application/json" -Body $body
```

命令会作用在**当前载入的投影**上。没有载入文件时先调用 `/api/load` 或 `/api/new`。

## 返回结构

```json
{
  "ok": true,
  "actor": "agent",
  "log": "WorldEdit CLI ...",
  "state": {
    "name": "untitled.schem",
    "source": "untitled.schem",
    "dirty": true,
    "revision": 8,
    "width": 16,
    "height": 16,
    "length": 16,
    "dataVersion": 3955,
    "formatVersion": 2,
    "palette": ["minecraft:air", "minecraft:stone"],
    "data": "base64-encoded varint block data",
    "blockCount": 1736,
    "totalBlocks": 4096
  }
}
```

- `state.data` 是 Sponge 方块索引的 varint 序列（Base64）；服务端不保存 base64 副本，读取时现编码。
- `revision` 用于判断状态新旧；每次成功写入都自增。
- 命令失败时通常仍是 HTTP 200，`ok:false`，并在 `log`/`error` 中说明；客户端应同时检查两者。
- `actor` 只是标签，不参与权限判断。

## 端点

| 方法 | 路径 | 请求 | 说明 |
|---|---|---|---|
| GET | `/api/state` | | `{ok, revision, state}`；空工作区 `state:null` |
| GET | `/api/files` | | `{ok, files:[{name,size,mtime,active,dirty}]}` |
| GET | `/api/events` | | SSE，见下 |
| GET | `/api/download?name=x.schem` | | 下载文件；不带 name 下载当前工作副本 |
| POST | `/api/load` | `{"name":"a.schem"}` | 载入源文件 |
| POST | `/api/new` | `{"name":"a.schem","width":16,"height":16,"length":16}` | 新建全空气投影 |
| POST | `/api/upload?name=a.schem` | 原始字节 | 上传 `.schem` |
| POST | `/api/rename` | `{"name":"a.schem","newName":"b.schem"}` | 重命名源文件 |
| POST | `/api/duplicate` | `{"name":"a.schem","newName":"b.schem"}` | 复制；不切换当前文件 |
| POST | `/api/delete` | `{"name":"a.schem"}` | 删除；当前文件会关闭 |
| POST | `/api/close` | `{}` | 关闭当前投影 |
| POST | `/api/save` | `{}` | 工作副本覆盖源文件 |
| POST | `/api/save-as` | `{"name":"b.schem","overwrite":true}` | 另存为并切换 |
| POST | `/api/reset` | `{}` | 源文件覆盖工作副本 |
| POST | `/api/run` | `{"commands":"...","actor":"agent"}` | 执行 WorldEdit |
| POST | `/api/reveal` | `{}` | 在资源管理器中打开 `schematics/` |

`/api/new` 尺寸范围 1–256；名称不能包含路径分隔符，`.schematic` 会被拒绝。上传同名文件会自动加
`_1`、`_2` 后缀。

## SSE 事件

`GET /api/events` 返回 `text/event-stream`：

```
retry: 1000

data: {"revision":8,"actor":"agent","state":{...},"files":[...]}
```

- 首次连接立即收到当前快照。
- 之后只在 revision 变化时发送；每 0.3s 检查一次。
- 事件中的 `state` 结构与 `/api/state` 的 `state` 相同。
- 浏览器 EventSource 自动重连；服务端在断线时结束该连接。
- 页面会把 `actor:"agent"` 的更新提示为「AI 已更新」。
- 大投影的快照包含完整 Base64 数据；局域网本机可接受，超大投影需要自行做增量/压缩。

## 命令行助手

```bat
python tools\agent_run.py --command "//pos1 0,0,0`n//pos2 3,3,3`n//set minecraft:stone"
python tools\agent_run.py --file commands.txt
python tools\agent_run.py --file commands.txt --actor my-agent
```

参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--command/-c` | | 命令字符串，换行分隔 |
| `--file/-f` | | 从文件读命令（推荐多行） |
| `--actor` | `agent` | SSE/页面提示标签 |
| `--url` | `http://127.0.0.1:8777` | 服务地址 |

工具会打印 WorldEdit 日志和 `ok/actor/revision/blocks/dirty` 摘要，`ok:false` 时退出码为 1。

## 并发与一致性

- `Workspace` 使用 `RLock`，同一时刻只有一个命令/文件操作在改状态。
- 命令执行期间 Web 页面显示 busy；外部 Agent 的更新在 busy 结束后应用到页面。
- 前端按 revision 去重：SSE 事件 revision 不大于当前状态时忽略。
- 命令超时 180s；超时会终止 JVM，返回 `ok:false`。
- 重新打开文件会丢弃当前未保存的 `work` 副本；先 `/api/save` 或 `/api/save-as`。

## 安全

- 默认没有 token；任何能访问 127.0.0.1:8777 的本机进程都能修改投影。
- 远程 Agent 建议通过 SSH 隧道、VPN 或反向代理加认证；不要直接端口映射。
- 文件名会做安全校验，禁止 `../` 和路径分隔符；上传有大小限制。
- 不要在页面/日志中放密钥；项目不读取任何 API key。

## 示例：轮询外部状态

没有 SSE 的客户端可以轮询：

```python
import json, time, urllib.request

BASE = "http://127.0.0.1:8777"
last = None
while True:
    with urllib.request.urlopen(BASE + "/api/state") as response:
        data = json.load(response)
    if data["revision"] != last:
        last = data["revision"]
        state = data["state"]
        if state:
            print(state["name"], state["blockCount"], state["revision"])
    time.sleep(0.5)
```
