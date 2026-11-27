# Nanke API · 接入说明

面向国内用户的 LLM 模型网关接入示例：一个 Key，OpenAI 兼容协议，改一行 `base_url` 就能接现成客户端。

- 站点：https://nanke.pro
- Base URL：`https://nanke.pw/v1`（国内直连，主推）／`https://nanke.pro/v1`（兼容）
- 模型与价格：https://nanke.pro/pricing （公开可查，无需登录）

本仓库只放**接入示例与踩坑说明**，不放密钥、不做镜像。

---

## 1. 三条命令验证能不能用

```bash
# 拉模型列表（需要你的令牌）
curl -s https://nanke.pw/v1/models \
  -H "Authorization: Bearer $NK_KEY" | head -c 500

# 非流式对话
curl -s https://nanke.pw/v1/chat/completions \
  -H "Authorization: Bearer $NK_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku","messages":[{"role":"user","content":"你好"}]}'

# 流式对话（注意检查 [DONE]）
curl -N https://nanke.pw/v1/chat/completions \
  -H "Authorization: Bearer $NK_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-haiku","stream":true,"messages":[{"role":"user","content":"你好"}]}'
```

## 2. 代码示例

- [`examples/python_openai.py`](examples/python_openai.py) — OpenAI SDK，含空流校验
- [`examples/node_openai.mjs`](examples/node_openai.mjs) — Node 20+，含重试与降级链
- [`examples/curl_stream.sh`](examples/curl_stream.sh) — 纯 curl 流式，排查用

## 3. 客户端接入

| 客户端 | 怎么改 | 备注 |
|---|---|---|
| Cursor | `Settings → Models → Override OpenAI Base URL` 填 `https://nanke.pw/v1`，然后手动 Add model | 模型名要和广场在架名一致 |
| Claude Code | 环境变量 `ANTHROPIC_BASE_URL=https://nanke.pw` + `ANTHROPIC_AUTH_TOKEN=<key>` | 走 `anthropic/` 前缀的原厂模型名 |
| Cline / Roo Code | 选 OpenAI Compatible，Base URL 同上 | 支持工具调用 |
| SillyTavern | 选 OpenAI 兼容，填 Base URL 与 Key | 长对话优先长上下文档 |
| LobeChat / Cherry Studio | 自定义 OpenAI 服务商 | — |
| Dify / FastGPT | 自定义 OpenAI 兼容模型 | 需要 `/v1/models` 可用 |

## 4. 模型分档（用名字就能认）

| 档位 | 名字形态 | 用途 |
|---|---|---|
| 免费福利 | `xxx:free` | 试 Prompt、跑 demo；排队限速，不保 SLA |
| 性价比 | 短名，如 `claude-3-haiku` | 轻量档，日常高频 |
| 多线号池 | `xxx:pool` | 多供应商容灾，单条故障自动切换 |
| 官方原厂 | `anthropic/` `openai/` `google/` 前缀 | 原厂直连，验真/高客单 |
| 更多模型 | 其余 `vendor/...`、`qwen*`、`glm*`、图片模型 | 长尾覆盖 |

## 5. 价格口径

- 按 token 计费，输入/输出分别计价，人民币结算
- 起步 ¥0.43 / 百万 token（轻量档）
- 命中缓存的部分按折扣价，实际账单通常低于标价
- 失败（超时 / 报错 / 空流）不计费

完整价目以 https://nanke.pro/pricing 为准，本仓库不承诺价格（价格会变，写死就是坑）。

## 6. 三个真实会踩的坑

**① HTTP 200 不等于成功。** 流式接口返回 200 但一个 token 都没有的情况很常见，必须校验内容与 `[DONE]`：

```python
got = False
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        got = True
if not got:
    raise RuntimeError("empty stream")
```

**② 模型名拼错不会降级，会 404。** 建议在代码里维护一份允许的模型名清单，不要让用户随便填。

**③ 便宜档和原厂档不是一个东西。** 同一个任务，档位选错账单差十几倍；先用免费档验证 Prompt，再按量升级。

## 7. 怎么验证一个中转站有没有换模型

这段与具体供应商无关，任何中转站都适用：

1. 固定一段有推理步骤的长 Prompt，官方直连与待测站各跑 20 次，比对输出长度分布、工具调用结构、`temperature=0` 下的一致性
2. 看 `usage` 字段是否完整（`prompt_tokens` / `completion_tokens` / 缓存命中字段）；缺字段或明显是估算值的要警惕
3. 看是否支持 prompt caching：原厂 API 的缓存读写单独计价，没有这个能力的"低价"其实不便宜

## 8. 联系我们

- 客服微信：`nanke_api`
- QQ 群：551961503（开发者）/ 1013093163（酒馆）
- 备案：鲁ICP备2026032613号-3 · 鲁公网安备37028202001381号

> 本仓库为官方接入说明，示例代码可自由复制使用。
