from rest_framework.routers import DefaultRouter
from survey.views import (
    QuizViewSet,

)

router = DefaultRouter()
router.register(r"", QuizViewSet, basename="quizzes")

urlpatterns = router.urls
