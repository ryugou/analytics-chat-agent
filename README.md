# analytics-chat-agent

自然言語でGoogle Analytics（GA4）のBigQueryデータを分析・可視化・予測するAIエージェント。

---

## 🎯 概要

`analytics-chat-agent` は、Google Analytics から BigQuery に同期されたイベントデータを対象に、ユーザーが自然言語で質問することで、以下の機能を提供します：

- 自然言語からの **SQL自動生成**
- **BigQuery実行結果の取得と整形表示**
- よくある質問に基づく **Few-shotテンプレート**
- 将来的には **KPI予測（XGBoost）** や **GPTによるインサイト提示** にも対応予定

---

## 🏗️ 構成（予定）
analytics-chat-agent/
├── backend/ # Python (LangChain + Qdrant + BigQuery)
│ ├── main.py
│ ├── queryEngine.py
│ ├── schemaEmbedder.py
│ └── .env.example
│
├── frontend/ # AngularJSベースのChat UI（今後追加）
├── docker-compose.yml # Qdrant用
├── requirements.txt
└── README.md

---

## 🚀 セットアップ手順（開発環境）

### 1. Python仮想環境の作成（推奨：Python 3.10〜3.11）

```bash
python -m venv .venv
source .venv/bin/activate
