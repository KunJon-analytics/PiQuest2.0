from rest_framework import routers
from .api import QuizViewSet

router = routers.DefaultRouter()
router.register('api/quiz', QuizViewSet, 'quiz')

urlpatterns = router.urls
