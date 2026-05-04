# import json
# from fastapi import APIRouter, Depends, HTTPException
# from app.schemas import ChatRequest, ChatCreateRequest, ChatResponse, IndexSelectRequest, PromptSelectRequest
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.services.auth_service import get_current_active_user
# from app.models.user import User
# from app.database import get_async_db
# from app.models import Chats
# from app.services.database_service import ChatService, AISetupService
# from app.utils.parse_utils import AIParser, load_json
# router = APIRouter(prefix="/chat", tags=["chat"])


# @router.post("/create")
# async def create_chat(data: ChatCreateRequest, db: AsyncSession = Depends(
#         get_async_db), current_user: User = Depends(get_current_active_user)):
#     """Create a new chat session"""
#     chat = await ChatService.create_chat(db, current_user.id, data.result_id)
#     return {
#         "id": str(chat.id),
#         "user_id": chat.user_id,
#         "result_id": chat.result_id,
#         "created_at": chat.created_at.isoformat(),
#         "active_indices": chat.active_indices or []
#     }


# @router.get("/for-result/{result_id}")
# async def get_or_create_chat_for_result(
#         result_id: int,
#         db: AsyncSession = Depends(get_async_db),
#         current_user: User = Depends(get_current_active_user)):
#     """Get or create a chat session for a specific result"""
#     chat = await ChatService.get_or_create_chat_for_result(db, current_user.id, result_id)
#     return {
#         "id": str(chat.id),
#         "user_id": chat.user_id,
#         "result_id": chat.result_id,
#         "created_at": chat.created_at.isoformat(),
#         "active_indices": chat.active_indices or []
#     }


# @router.post("/select-index")
# async def select_index(data: IndexSelectRequest, db: AsyncSession = Depends(get_async_db)):
#     chat = await db.get(Chats, str(data.chat_id))
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     if data.index_name:
#         if chat.active_indices is None:
#             chat.active_indices = []

#         if data.index_name not in chat.active_indices:
#             chat.active_indices.append(data.index_name)

#     await db.commit()

#     return {"status": "ok", "active_indices": chat.active_indices}


# @router.post("/unselect-index")
# async def unselect_index(data: IndexSelectRequest, db: AsyncSession = Depends(get_async_db)):
#     chat = await db.get(Chats, str(data.chat_id))
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     if data.index_name and chat.active_indices:
#         chat.active_indices = [idx for idx in chat.active_indices if idx != data.index_name]

#     await db.commit()

#     return {"status": "ok", "active_indices": chat.active_indices}


# @router.post("/select-prompt")
# async def select_prompt(data: PromptSelectRequest, db: AsyncSession = Depends(get_async_db)):
#     chat = await db.get(Chats, str(data.chat_id))
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     prompt = await AISetupService.get_prompt(db, data.prompt_source)
#     if not prompt:
#         raise HTTPException(status_code=404, detail="Prompt not found")

#     await db.commit()

#     return {"status": "ok"}


# @router.post("/message")
# async def chat_message(
#         data: ChatRequest,
#         db: AsyncSession = Depends(get_async_db),
#         current_user: User = Depends(get_current_active_user),
#         response_model=ChatResponse):
#     chat = await db.get(Chats, data.chat_id)
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     context_history = await ChatService.get_chat_messages(db, current_user.id, data.chat_id)

#     result_context = None
#     result = None
#     if chat.result_id:
#         result = await db.get(ShodanResult, chat.result_id)
#         if result:
#             indices_info = []
#             if result.indices:
#                 for idx in result.indices:
#                     if idx.get('size_bytes') is not None and idx.get('size_bytes') < 10 * 1024 * 1024:
#                         continue
#                     indices_info.append({
#                         "name": idx.get("name"),
#                         "size": idx.get("size"),
#                         "docs": idx.get("docs"),
#                         "size_bytes": idx.get("size_bytes")
#                     })

#             result_context = {
#                 "ip_address": result.ip_address,
#                 "port": result.port,
#                 "org": result.org,
#                 "country_code": result.country_code,
#                 "total_docs": result.total_docs,
#                 "data_size_bytes": result.data_size_bytes,
#                 "indices": indices_info
#             }

#             # Initialize indices_context
#             indices_context = ''
#             if chat.active_indices:
#                 ip_address = result.ip_address
#                 for index in chat.active_indices:
#                     index_context = await load_json(index, ip_address)
#                     indices_context += f"\n\n---\n\n**Index: {index}**\n{index_context}"
#                     if chat.per_index_history:
#                         hist = next((h['messages'] for h in chat.per_index_history if h['index'] == index), [])
#                         for msg in hist:
#                             role = "User" if msg['role'] == 'user' else "Assistant"
#                             indices_context += f"\n[{role}]: {msg['content']}"
#         else:
#             indices_context = ''
#     else:
#         indices_context = ''

#     prompt_source = data.prompt_source or "chat"
#     parser = AIParser(source=prompt_source)

#     indices_summary = ""
#     if result_context:
#         indices_summary = (
#             f"[Result Context: IP={result_context['ip_address']}, "
#             f"Indices={len(result_context['indices'])}, "
#             f"Total Docs={result_context['total_docs']}]\n\n"
#             "Indices:\n"
#         )
#         for idx in result_context['indices']:
#             indices_summary += f"- {idx['name']} ({idx['size']}, {idx['docs']} docs)\n"

#     if prompt_source == "base_ai_query" and result_context and result:
#         dataset_index_lines = []
#         for idx in result_context['indices']:
#             dataset_index_lines.append(f"- {idx['name']}({idx['size']})")

#         selected_indices = chat.active_indices or [idx['name'] for idx in result_context['indices'][:10]]
#         selected_indices = selected_indices[:10]

#         samples_section_parts = []
#         for index_name in selected_indices:
#             try:
#                 index_samples = await load_json(index_name, result.ip_address)
#                 if index_samples:
#                     samples_section_parts.append(
#                         f"Dataset: {index_name}\nSamples:\n{json.dumps(index_samples[:10])}"
#                     )
#             except FileNotFoundError:
#                 continue
#             except Exception:
#                 continue

#         samples_block = "\n\n".join(
#             samples_section_parts) if samples_section_parts else "No sample files found for selected indices."
#         dataset_index_block = "\n".join(
#             dataset_index_lines) if dataset_index_lines else "No dataset index information available."

#         final_prompt = (
#             "Dataset index:\n"
#             f"{dataset_index_block}\n\n"
#             "Sample data (up to 10 datasets, first records):\n"
#             f"{samples_block}"
#         )
#     else:
#         final_prompt = (
#             indices_summary +
#             "\n\nSelected Indices Context:\n" +
#             indices_context +
#             f"\n\nUser Question:\n{data.message}"
#         )

#     ai_response = parser.call_ai(final_prompt, history=context_history)

#     await ChatService.create_message(
#         db,
#         data.chat_id,
#         data.message,
#         role="user",
#         active_indices=chat.active_indices or [],
#     )
#     if isinstance(ai_response, dict):
#         answer = ai_response.get('answer') or ai_response.get('text') or 'No response'
#         explanation = ai_response.get('explanation')
#         score = ai_response.get('score') if isinstance(ai_response.get(
#             'score'), int) or ai_response.get('score') is None else None
#         confidence = ai_response.get('confidence') if isinstance(ai_response.get('confidence'), int) else None
#     else:
#         answer = str(ai_response)
#         explanation = None
#         score = None
#         confidence = None

#     if prompt_source == "base_ai_query" and result and confidence is not None:
#         result.ai_score = score
#         result.confidence = confidence
#         await db.commit()

#     message_parts = [answer]
#     if prompt_source == "base_ai_query" and confidence is not None:
#         score_display = str(score) if isinstance(score, int) else "null"
#         message_parts.append(
#             f"\n\n**Scoring:**\n- Score: {score_display}/5\n- Confidence: {confidence}/5"
#         )
#     if explanation:
#         message_parts.append(f"\n\n---\n\n**Explanation:** {explanation}")
#     message_content = '\n'.join(message_parts)

#     await ChatService.create_message(
#         db,
#         data.chat_id,
#         message_content,
#         role="assistant",
#         active_indices=chat.active_indices or [],
#     )
#     if chat.active_indices:
#         if chat.per_index_history is None:
#             chat.per_index_history = []

#         for index in chat.active_indices:
#             hist_entry = next((h for h in chat.per_index_history if h["index"] == index), None)
#             if not hist_entry:
#                 hist_entry = {"index": index, "messages": []}
#                 chat.per_index_history.append(hist_entry)

#             hist_entry["messages"].append({"role": "user", "content": data.message})
#             hist_entry["messages"].append({"role": "assistant", "content": answer})

#         await db.commit()
#     return ChatResponse(answer=answer, explanation=explanation, score=score, confidence=confidence)


# @router.get("/history/{chat_id}")
# async def get_chat_history(chat_id: str, db: AsyncSession = Depends(get_async_db),
#                            current_user: User = Depends(get_current_active_user)):
#     return await ChatService.get_chat_messages(db, current_user.id, chat_id)
