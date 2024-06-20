import json

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from api.tools.llm import send_question_to_llm
from api.tools.main_tools import (add_data_to_faiss, create_document,
                                  remove_data_from_faiss, update_meetings)

from .models import Contact, CustomerContext, Lead
from .serializers import (AddDataSerializer, ContactSerializer,
                          QuestionSerializer, LeadSerializer)


class OtwChatbotView(APIView):
    def get_view_name(self):
        return "OTW AI Chatbot"

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            chat_id = serializer.validated_data['chat_id']
            question = serializer.validated_data['question']
            customer_id = serializer.validated_data['customer_id']
            try:
                answer, chat_history, questions_asked, response = send_question_to_llm(question, chat_id, customer_id)
                return Response({
                    'answer': answer,
                    'questions_asked': questions_asked,
                    'chat_history': chat_history,
                    'llm_response': response,
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDataView(APIView):
    def post(self, request):
        serializer = AddDataSerializer(data=request.data)
        if serializer.is_valid():
            context_title = serializer.validated_data['title']
            try:
                # Add context to database
                serializer.create(serializer.data)
                context_id = CustomerContext.objects.last().id

                document = serializer.save(context_id)

                # Update meetings
                update_meetings()

                # Add document to FAISS
                add_data_to_faiss(document, chunk_size=4000, chunk_overlap=200, path="db/customers_contexts", )

                return Response(
                    f'Context was successfully created! Metadata: [Title: {context_title}, Context ID: {context_id}].',
                    status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        context_id = request.query_params.get('context_id')
        if not context_id:
            return Response({'error': 'Parameter context_id is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            context = CustomerContext.objects.get(id=context_id)
            context.delete()

            response_from_faiss = remove_data_from_faiss(context_id, metadata_tag="context_id",
                                                         path="db/customers_contexts")

            return Response(f'Context with context_id: {context_id} was successfully deleted. {response_from_faiss}',
                            status=status.HTTP_200_OK)
        except CustomerContext.DoesNotExist:
            return Response({'error': f'Context with context_id {context_id} not found. Please check context_id.'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactViewSet(APIView):
    def post(self, request):
        try:
            contact_id = request.data.get('contact_id')
            contact = Contact.objects.get(contact_id=contact_id)
            serializer = ContactSerializer(contact, data=request.data)
            # Удаление старых данных из FAISS при обновлении
            remove_data_from_faiss(contact_id, metadata_tag="contact_id", path="db/contacts")
            is_update = True
        except Contact.DoesNotExist:
            serializer = ContactSerializer(data=request.data)
            is_update = False

        if serializer.is_valid():
            serializer.save()
            metadata = {'contact_id': serializer.data['contact_id']}
            document_context = json.dumps(serializer.data)
            document = create_document(document_context, metadata)
            add_data_to_faiss(document, chunk_size=700, chunk_overlap=100, path="db/contacts")

            return Response(
                f'Contacts have been successfully {"updated" if is_update else "created"}! {serializer.data}',
                status=status.HTTP_200_OK if is_update else status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        contact_id = request.query_params.get('contact_id')
        if not contact_id:
            return Response({'error': 'Parameter contact_id is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            context = Contact.objects.get(contact_id=contact_id)
            context.delete()

            remove_data_from_faiss(contact_id, metadata_tag="contact_id", path="db/contacts")

            return Response(f'Contact_id: {contact_id} was successfully deleted.',
                            status=status.HTTP_200_OK)
        except CustomerContext.DoesNotExist:
            return Response({'error': f'Context with contact_id {contact_id} not found. Please check contact_id.'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
