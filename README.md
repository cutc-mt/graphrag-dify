# graphrag-dify
このビデオはAI带路党Proがビデオ共有のために準備したものです[おそらくGraphRAGとDifyを組み合わせた最初のチュートリアル-GraphRAG実践チュートリアル2](https://www.bilibili.com/video/BV1ud1iY3Em1)
graphragをhttpサービスとして公開し、difyで使用します

**注意:このリポジトリのコードはgraphragのソースコードと一緒に配置する必要があります**

### リリースログ
2024.12.11更新
公式v0.9.0バージョンをサポート
### 公式ソースコードをチェックアウト

```bash
# コードをクローン
git clone https://github.com/microsoft/graphrag.git 
# ディレクトリに移動
cd graphrag
# v0.9.0バージョンに切り替え
git checkout v0.9.0
```

### 準備作業

pyproject.tomlに依存パッケージを追加し、poetry installを実行します
```
fastapi = "^0.115.0"
uvicorn = "^0.31.0"
asyncio = "^3.4.3"
utils = "^1.0.2"
```
### ファイルの配置場所
- main.py はgraphragプロジェクトのソースコードのルートディレクトリに配置します
- search.pyとsearch_prompt.pyはリポジトリ内のディレクトリ構造に従ってgraphragのソースファイルを上書きします
- 生成されたインデックスはルートディレクトリのindexsディレクトリに配置します

### テスト

- response typeにsearch_promptパラメータが追加されました。公式コマンドを参考に、正常に動作するかテストしてください

### graphragサービスの起動
> poetry shell
> 
> uvicorn main:app --reload --host 0.0.0.0 --port 8000
### dify dslのインポート
- difyの2つのdslをインポートし、ワークフローをツールとして再公開し、agentで再参照します。詳細はビデオを参照してください