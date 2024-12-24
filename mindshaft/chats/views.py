from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Chat, Message, ChatParticipant
from users.utils import consume_credits
from .serializers import ChatSerializer, MessageSerializer, CreateChatSerializer, AddMessageSerializer
from django.conf import settings
from rag.utils import get_relevant_context
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os
# Chroma DB Directory
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')
os.environ["OPENAI_API_KEY"]=settings.OPENAI_API_KEY

class UserChatsView(APIView):
    """
    View to list all chats related to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        chats = user.get_all_user_chats()
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class ChatMessagesView(APIView):
    """
    View to list all messages of a specific chat.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id, *args, **kwargs):
        chat = get_object_or_404(Chat, id=chat_id)

        # Ensure the user is a participant of the chat
        if not chat.participants.filter(user=request.user).exists():
            return Response({"error": "You are not a participant of this chat."}, status=403)

        messages = chat.get_all_messages()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class CreateChatView(APIView):
    """
    View to create a new chat with the logged-in user as the owner.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Add the logged-in user as the owner of the chat
        chat_data = request.data.copy()
        chat_data['user'] = request.user.id  # Set the logged-in user as the chat owner
        print(chat_data)
        serializer = CreateChatSerializer(data=chat_data)
        if serializer.is_valid():
            chat = serializer.save(user=request.user)

            # Automatically add the logged-in user as a participant
            ChatParticipant.objects.create(chat=chat, user=request.user)

            return Response({
                'id': chat.id,
                'name': chat.name,
                'owner': request.user.email,
                'participants': [request.user.email]  # Default participant list with the owner
            }, status=201)
        return Response(serializer.errors, status=400)


class AddMessageView(APIView):
    """
    View to add a message to a chat owned by the logged-in user and generate an AI response.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id, *args, **kwargs):
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            raise PermissionDenied("You do not have permission to add messages to this chat.")

        # Add the user's message to the chat
        message_data = request.data.copy()
        message_data['chat'] = chat.id
        message_data['user'] = request.user.id

        

        serializer = MessageSerializer(data=message_data)
        if serializer.is_valid():
            user_message = serializer.save()

            # Generate AI response
            ai_response = self.generate_ai_response(user_message.content, chat)
    
            response_json = ai_response.dict()
            response_metadata = response_json['response_metadata']
            token_usage = response_metadata['token_usage']
            total_tokens = token_usage['total_tokens']
         
            msg_content = response_json['content'].strip()
            consume_credits(request.user, total_tokens)

            # Save AI response as a message
            if ai_response:
                Message.objects.create(
                    chat=chat,
                    user=None,  # No user for AI messages
                    content=msg_content,
                    is_system_message=True
                )

            return Response({
                "id": user_message.id,
                "chat": chat.id,
                "user": request.user.email,
                "content": user_message.content,
                "ai_response": msg_content,  # Include AI response in the API response
                "created_at": user_message.created_at,
                "tokens_used": total_tokens
            }, status=201)
        return Response(serializer.errors, status=400)

    def generate_ai_response(self, user_message, chat):
        """
        Generate an AI response using LangChain's RunnableSequence with ChatOpenAI.
        """
        try:
            # Initialize the OpenAI Chat model
            chat_model = ChatOpenAI(
                temperature=0.1,
                openai_api_key=settings.OPENAI_API_KEY,
                model="gpt-4o-mini"
            )

            # Check if Chroma DB exists and get context if available
            if os.path.exists(CHROMA_DB_DIR):
                context = get_relevant_context(user_message)
            else:
                context = "No relevant context available."

            # Define the prompt template
            prompt_template = PromptTemplate(
                input_variables=["context", "history", "user_message"],
                template="""
You are a compassionate mental health professional helping a client. Do not suggest any medicines.
Use the following context to inform your response, if relevant:

{context}

Conversation History:
{history}
Client: {user_message}
Therapist:"""
            )

            # Create the sequence
            chain = prompt_template | chat_model

            # Get conversation history
            history = self.get_conversation_history(chat)

            # Run the chain with the provided inputs
            inputs = {
                "context": context,
                "history": history,
                "user_message": user_message
            }
            response = chain.invoke(inputs)
            print(response)
            return response  # Ensure a clean response
        except Exception as e:
            print(f"AI response generation error: {e}")
            return "I'm sorry, but I'm unable to provide a response at this time."

    def get_conversation_history(self, chat):
        """
        Retrieve the conversation history for the chat.
        """
        messages = Message.objects.filter(chat=chat).order_by("created_at")
        history = ""
        for msg in messages:
            sender = "Client" if msg.user else "Therapist"
            history += f"{sender}: {msg.content}\n"
        return history
    




#     class AddMessageViewStream(APIView):
#     """
#     View to add a message to a chat owned by the logged-in user and generate an AI response with streaming.
#     """
#     permission_classes = [IsAuthenticated]

#     def post(self, request, chat_id, *args, **kwargs):
#         try:
#             chat = Chat.objects.get(id=chat_id, user=request.user)
#         except Chat.DoesNotExist:
#             raise PermissionDenied("You do not have permission to add messages to this chat.")

#         # Add the user's message to the chat
#         message_data = request.data.copy()
#         message_data['chat'] = chat.id
#         message_data['user'] = request.user.id

#         serializer = MessageSerializer(data=message_data)
#         if serializer.is_valid():
#             user_message = serializer.save()

#             # Generate streaming AI response
#             response = self.stream_ai_response(user_message.content, chat)

#             return StreamingHttpResponse(
#                 response,
#                 content_type="text/event-stream",
#                 status=200
#             )
#         return Response(serializer.errors, status=400)

#     def stream_ai_response(self, user_message, chat):
#         """
#         Stream an AI response using OpenAI's ChatCompletion API.
#         """
#         try:
#             # Initialize the OpenAI API key
#             openai.api_key = settings.OPENAI_API_KEY

#             # Check if Chroma DB exists and get context if available
#             if os.path.exists(CHROMA_DB_DIR):
#                 context = get_relevant_context(user_message)
#             else:
#                 context = "No relevant context available."

#             # Get conversation history
#             history = self.get_conversation_history(chat)

#             # Prepare the prompt
#             prompt = f"""
# You are a compassionate mental health professional helping a client. Do not suggest any medicines.
# Use the following context to inform your response, if relevant:

# {context}

# Conversation History:
# {history}
# Client: {user_message}
# Therapist:"""

#             # Stream the response from OpenAI's ChatCompletion
#             response = openai.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "system", "content": prompt}],
#                 temperature=0.1,
#                 stream=True
#             )

#             for chunk in response:
#                 chunk = chunk.model_dump(mode="json")
#                 if 'choices' in chunk:
#                     choice = chunk["choices"][0]
#                     delta = choice.get("delta", {})
#                     content = delta.get("content")
#                     if content:
#                         yield f"data: {content}\n\n"

#             # Send a stop signal when the response is complete
#             yield "data: [END OF RESPONSE]\n\n"
#         except Exception as e:
#             print(f"AI streaming error: {e}")
#             yield "data: I'm sorry, but I'm unable to provide a response at this time.\n\n"

#     def get_conversation_history(self, chat):
#         """
#         Retrieve the conversation history for the chat.
#         """
#         messages = Message.objects.filter(chat=chat).order_by("created_at")
#         history = ""
#         for msg in messages:
#             sender = "Client" if msg.user else "Therapist"
#             history += f"{sender}: {msg.content}\n"
#         return history


