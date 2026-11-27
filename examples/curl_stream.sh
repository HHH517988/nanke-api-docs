#!/usr/bin/env bash
# 纯 curl 流式排查：看有没有内容、有没有 [DONE]
# NK_KEY=sk-xxx bash curl_stream.sh
set -u

: "${NK_KEY:?set NK_KEY first}"
BASE="${BASE:-https://nanke.pw/v1}"
MODEL="${MODEL:-claude-3-haiku}"

curl -sN "$BASE/chat/completions" \
  -H "Authorization: Bearer $NK_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"说一句话\"}]}" \
  | tee /tmp/nk_stream.txt \
  | grep -c '^data:' 

echo "--- 事件数上面，下面是结尾三行 ---"
tail -n 3 /tmp/nk_stream.txt

if grep -q '\[DONE\]' /tmp/nk_stream.txt; then
  echo "OK: 收到 [DONE]"
else
  echo "WARN: 没收到 [DONE]，流可能被截断"
fi
