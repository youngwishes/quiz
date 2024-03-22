from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response

from survey.serializers import (
    QuizSerializer, QuizListSerializer
)
from survey.models import (
    Quiz,
)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.prefetch_related("questions", "questions__answers")
    serializer_class = QuizSerializer
    http_method_names = ["get", "post", "put", "delete"]

    def list(self, request: Request, *args, **kwargs) -> Response:
        serializer = QuizListSerializer(self.queryset, many=True)
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)
