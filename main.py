# FastAPIをインポート
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from neo4j import GraphDatabase
from ms_graphrag_neo4j import MsGraphRAG
import uvicorn
from openai import AsyncOpenAI, AsyncAzureOpenAI

class SearchQuery(BaseModel):
    query: str

# FastAPIインスタンスを作成
app = FastAPI()

# Neo4jドライバの初期化
if not all(os.environ.get(var) for var in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]):
    raise ValueError("Neo4jの接続情報（NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD）が設定されていません。")

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
)

@app.post("/v1/search")
async def search(search_query: SearchQuery):
    """
    Neo4jグラフで検索を実行し、LLMを使用して回答を生成します。
    """
    try:
        # LLMクライアントの初期化
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if azure_endpoint:
            # Azure OpenAIを使用
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            api_version = os.environ.get("OPENAI_API_VERSION")
            deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
            if not all([api_key, api_version, deployment]):
                raise ValueError("Azure OpenAIを使用するには、AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENTの環境変数が必要です。")
            
            llm_client = AsyncAzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
            )
            model = deployment
        else:
            # 標準のOpenAIを使用
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY環境変数が必要です。")
            llm_client = AsyncOpenAI(api_key=api_key)
            model = "gpt-4o" # または他の希望するモデル

        # MsGraphRAGのインスタンスを作成し、クライアントとモデルをモンキーパッチ
        ms_graph = MsGraphRAG(driver=driver)
        ms_graph._openai_client = llm_client
        ms_graph.model = model

        # 1. グラフからすべてのエンティティを取得
        entities_result = ms_graph.query("MATCH (e:__Entity__) RETURN e.name AS name, e.summary AS summary")
        all_entities = {item['name']: item['summary'] for item in entities_result if item['name']}

        # 2. クエリ内で言及されているエンティティを見つける
        mentioned_entities = {
            name: summary
            for name, summary in all_entities.items()
            if name.lower() in search_query.query.lower()
        }

        context_str = ""
        if mentioned_entities:
            # 3. コンテキストを取得
            for entity_name, summary in mentioned_entities.items():
                context_str += f"エンティティ: {entity_name}\n概要: {summary}\n\n"

                # 近隣エンティティとコミュニティの情報を取得
                neighbor_query = """
                MATCH (e:__Entity__ {name: $name})-->(neighbor)
                RETURN neighbor.name AS neighbor_name, neighbor.summary AS neighbor_summary
                """
                neighbors = ms_graph.query(neighbor_query, params={"name": entity_name})
                for neighbor in neighbors:
                    context_str += f"関連エンティティ: {neighbor['neighbor_name']}\n概要: {neighbor['neighbor_summary']}\n\n"

                community_query = """
                MATCH (e:__Entity__ {name: $name})-[:IN_COMMUNITY]->(c:__Community__)
                RETURN c.summary AS community_summary
                """
                communities = ms_graph.query(community_query, params={"name": entity_name})
                for community in communities:
                    context_str += f"コミュニティの概要: {community['community_summary']}\n\n"
        else:
            # 言及されているエンティティがない場合は、一般的なグラフの概要を使用
            reports = ms_graph.query("MATCH (r:__Report__) RETURN r.report as report")
            context_str = "\n".join([report['report'] for report in reports])

        # 4. LLMで回答を生成
        prompt = f"""
以下のコンテキスト情報に基づいて、質問に答えてください。

コンテキスト:
{context_str}

質問: {search_query.query}

回答:"""

        messages = [
            {"role": "system", "content": "あなたは、提供されたコンテキストに基づいて質問に答えるアシスタントです。"},
            {"role": "user", "content": prompt}
        ]

        response = await ms_graph.achat(messages)
        return {"result": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'llm_client' in locals() and hasattr(llm_client, 'close'):
            await llm_client.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)