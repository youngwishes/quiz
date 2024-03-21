from rest_framework import viewsets
from rest_framework import mixins
from survey.models import Survey
from survey.serializers import SurveySerializer


class SurveyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
