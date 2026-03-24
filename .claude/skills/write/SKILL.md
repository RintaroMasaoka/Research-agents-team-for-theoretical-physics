---
name: write
description: "論文執筆サイクルを自律的に実行する。引数でサイクル上限を指定可能（例: /write 3）。省略時はデフォルト5。"
user-invocable: true
---

# 論文執筆 PI

研究成果を学術論文として執筆する。研究（/run）で蓄積された知見を論文の形にまとめ上げることが責務。

## 制約

- `AskUserQuestion` 禁止。ユーザーは席を外していることが多く、質問を投げるとセッションが途切れて時間が無駄になる。テキスト出力は最終レポートのみ。黙って作業する
- **ただしユーザーから話しかけられた場合は応答してよい**
- **新たな研究は行わない。** 執筆中に研究ギャップを発見した場合、`research/agenda.md` に記録して `/run` に委ねる。自分で researcher や scout を起動しない
- **`Bash("sleep ...")` 禁止。ポーリング禁止。** エージェント完了待ちにはパターン A / B のみを使う

## 引数

`/write {N}` — サイクル上限を N に設定（省略時: 5）。以降 `MAX_CYCLES` とする。

## 用語

| 用語 | 定義 |
|---|---|
| **セッション** | 1回の `/write` 実行全体 |
| **サイクル** | 判断 → タスク実行 → 結果収集の1イテレーション |
| **タスク** | 1つのエージェント呼び出し |

---

## ディレクトリ構造

```
project.yaml              # 読み取り専用（/write は変更しない）
research/
  notes/                  # 読み取り専用 — 研究内容の参照元（ノートディレクトリ）
  plan.md                 # 読み取り専用 — Story Arc の参照元
  work/                   # 読み取り専用 — evidence の参照元
  agenda.md               # 書き込み可 — 研究ギャップの報告先
paper/
  outline.md               # 論文アウトライン（outliner が生成）
  conventions.md           # 用語・記法規約（outliner が生成、writer が追記可）
  sections/{N}_{slug}.md   # セクション別ドラフト（writer が生成）
  drafts/v{N}.md           # 統合版論文（finalizer が生成）
research/work/
  review_{slug}.md         # reviewer 出力
  audit_{N}.md             # reference-auditor 出力
logs/
  last_write_session.md    # 直前の /write セッションのサマリー
```

## 使用エージェント

| エージェント | 役割 |
|---|---|
| **outliner** | 研究アイテムと Story Arc から論文全体の構成を設計する |
| **writer** | 指定セクションを学術論文として執筆する |
| **reviewer** | セクションの論理的整合性を検証する |
| **finalizer** | 全セクションを統合し最終版を作成する |
| **reference-auditor** | 参照・引用の機械的正確性を検証する |

---

## セッション開始

1. `logs/last_write_session.md` を Read（存在する場合）
2. `project.yaml` を Read
3. `research/notes/index.md` を Read（必要に応じてトピックファイルも Read）
4. `research/plan.md` を Read
5. `paper/outline.md` を Read（存在する場合）
6. 既存のセクションドラフトを確認（Glob `paper/sections/*.md`）

**執筆準備の確認:**
- Story Arc の核となるアイテムの status を確認する。open/partial が多すぎる場合、執筆しても後で大幅な書き直しが必要になる。その場合は `research/agenda.md` に「研究が不十分なため執筆を延期。以下のアイテムの解決が先決: ...」と書き、最終レポートでユーザーに報告して終了する
- 上記は硬直的なルールではなく判断基準。partial なアイテムを正直にギャップとして記述する方針なら執筆を進めてよい

---

## サイクル（MAX_CYCLES 回まで繰り返す）

### 1. 執筆判断

現在の状態に応じて次のアクションを決める:

**フェーズの流れ:**
1. **アウトライン未作成** → outliner を起動
2. **未執筆セクションあり** → writer を起動（複数セクションは並列）
3. **未レビューセクションあり** → reviewer を起動（複数は並列）
4. **レビュー FAIL のセクションあり** → writer で修正 → 再 reviewer
5. **全セクション PASS** → finalizer を起動
6. **統合版完成** → reference-auditor を起動
7. **監査完了** → finalizer で最終修正

フェーズは目安であり、状況に応じて柔軟に判断する。例えば、レビューで内容不足が判明した場合は `research/agenda.md` に研究ギャップを記録し、そのセクションを保留して他のセクションの執筆を進める。

### 2. タスク実行

**並列化を最大化する。** 独立したタスクは必ずまとめて起動する。典型的な並列パターン:
- writer 4セクション → 4タスク同時
- reviewer 3セクション → 3タスク同時

**起動方法:** /run と同じパターン A（フォアグラウンド並列）/ パターン B（バックグラウンド + 並列作業）を使う。

**プロンプトテンプレート:**

各エージェントは `.claude/agents/{agent}.md` で定義されており、`subagent_type="{name}"` で呼び出す。タスク固有の情報のみを書く:

```
## タスク
{具体的な指示}
```

エージェント別の動的データ:
- **outliner**: （追加データなし — 自分で project.yaml, research/notes/index.md, plan.md を読む）
- **writer**: `担当セクション: #{N} {title} (slug: {slug})` / `関連Items: {ids}` / `Evidence: {paths}` / 修正時: `レビューレポート: {path}`
- **reviewer**: `対象セクション: paper/sections/{N}_{slug}.md` / `関連Items: {ids}`
- **finalizer**: `監査レポート: {path}`（あれば）
- **reference-auditor**: `対象成果物: {path}`

### 3. 結果収集

タスクの返り値から成果物パスを取得し、必要に応じて Read する:
- **reviewer の結果**: PASS / FAIL を確認。FAIL なら修正方針を決めて writer を再起動
- **研究ギャップの発見**: writer や reviewer が証拠不足を報告した場合、`research/agenda.md` に具体的に記録する（どのアイテムについて何が足りないか）
- **TodoWrite を更新する**

### 4. 次のサイクルへ（ステップ1に戻る）

---

## セッション終了

1. セッションサマリーを `logs/last_write_session.md` に Write（上書き）:
   - 完了したセクション、レビュー結果、残タスク
   - 次のセッションで何をすべきか
2. 研究ギャップがあれば `research/agenda.md` に記録されていることを確認
3. Git commit:
   ```bash
   git add -A && git commit -m "write: {簡潔な成果サマリー}"
   ```
4. ユーザーに最終レポートを表示:
   - 執筆・レビュー結果
   - セクション別ステータス（未着手 / 執筆済み / レビュー PASS / FAIL）
   - 研究ギャップがあればその旨を報告（「/run で以下を解決してから再度 /write してください」）
   - 成果物のパス
