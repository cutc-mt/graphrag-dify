# プロジェクト概要

このプロジェクトは、MicrosoftのGraphRAGをDifyで使用するためのFastAPIサービスとして公開します。これにより、Difyワークフロー内でGraphRAGのグラフベースの検索および生成機能を使用できます。

このプロジェクトは、特定のバージョンのGraphRAG（v0.9.0）で動作するように構成されており,検索プロンプトを直接返すサポートのためにGraphRAGソースコードに変更が加えられています。

含まれているDify YAMLファイル（`king_of_glory_agent.yml`および`king_of_glory_knowledge_base.yml`）は、このサービスをDifyと統合して「王者栄耀」（King of Glory）ナレッジベースエージェントを作成する例を提供します。

# ビルドと実行

1.  **GraphRAGのクローン:**
    ```bash
    git clone https://github.com/microsoft/graphrag.git
    cd graphrag
    git checkout v0.9.0
    ```

2.  **依存関係のインストール:**
    `graphrag`ディレクトリの`pyproject.toml`に次の依存関係を追加し、`poetry install`を実行します:
    ```
    fastapi = "^0.115.0"
    uvicorn = "^0.31.0"
    asyncio = "^3.4.3"
    utils = "^1.0.2"
    ```

3.  **ファイルの配置:**
    *   `main.py`を`graphrag`ディレクトリのルートに配置します。
    *   `search.py`と`search_prompt.py`を`graphrag/query/structured_search/local_search/`にコピーし、元のファイルを上書きします。
    *   GraphRAGインデックスを`graphrag`ディレクトリのルートにある`indexs`という名前のディレクトリに配置します。

4.  **サービスの実行:**
    ```bash
    poetry shell
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

# 開発規約

*   このプロジェクトでは、Webサービスの作成にFastAPIを使用しています。
*   コアロジックは`main.py`ファイル内にあり、APIリクエストを処理してGraphRAGライブラリを呼び出します。
*   このプロジェクトは、ローカル検索に`search_prompt`の`response_type`を追加するためにGraphRAGソースコードを変更します。これは、LLMに送信されるコンテキストのデバッグと理解に役立ちます。
*   Dify統合は、DifyプロジェクトにインポートできるYAMLファイルで定義されます。