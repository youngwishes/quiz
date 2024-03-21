from rest_framework.routers import DefaultRouter
from survey.views import SurveyViewSet
from django.urls import include, path


router = DefaultRouter()

router.register("survey", SurveyViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
