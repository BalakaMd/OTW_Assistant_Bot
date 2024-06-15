import json

from langchain_core.documents import Document
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.tools.llm import send_question_to_llm
from api.tools.main_tools import (add_data_to_faiss, create_document,
                                  remove_data_from_faiss)

from .models import Contact, CustomerContext
from .serializers import (AddDataSerializer, ContactSerializer,
                          QuestionSerializer)


class OtwChatbotView(APIView):
    def get_view_name(self):
        return "OTW AI Chatbot"

    def post(self, request):
        chat_id = request.headers.get('ChatID')
        if not chat_id:
            return Response({'error': 'ChatID is missing in headers.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
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
            customer_id = serializer.validated_data['customer_id']
            customer_name = serializer.validated_data['customer_name']
            document = serializer.save()
            if not isinstance(document[0], Document):
                return Response({'error': f'Code: {document}. Incorrect URL or no access to the file.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    # Add context to database
                    context, created = CustomerContext.objects.get_or_create(customer_id=customer_id)
                    context.data.append({'context': document[0].page_content})
                    context.customer_name = customer_name
                    context.save()

                    # Add document to FAISS
                    add_data_to_faiss(document, chunk_size=4000, chunk_overlap=200, path="db/customers_contexts", )

                    return Response(f'Context was successfully created! Metadata: [customer_id: {customer_id}]',
                                    status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'Parameter customer_id is missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Find the context and delete it
            context = CustomerContext.objects.get(customer_id=customer_id)
            context.delete()

            # Assuming you need to remove data from FAISS as well
            remove_data_from_faiss(customer_id, metadata_tag="customer_id", path="db/customers_contexts")

            return Response(f'Context with customer_id: {customer_id} was successfully deleted.',
                            status=status.HTTP_200_OK)
        except CustomerContext.DoesNotExist:
            return Response({'error': f'Context with customer_id {customer_id} not found. Please check customer_id.'},
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
