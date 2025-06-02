# analytics-chat-agent

自然言語でGoogle Analytics（GA4）のBigQueryデータを分析・予測するAIエージェント。

---

## 📁 ディレクトリ構成

analytics-chat-agent/
├── backend/ # Python: LangChain / Qdrant / BigQuery
│ ├── requirements.txt
│ ├── .env.example
│ └── ...
├── frontend/ # AngularJS UI（将来追加）
├── docker-compose.yml # Qdrant用
└── README.md # このファイル

---

## 🚀 セットアップ（バックエンド）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env



