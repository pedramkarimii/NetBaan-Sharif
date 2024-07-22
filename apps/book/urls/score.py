from django.urls import path
from apps.book.views import score

urlpatterns = [
    path('score-add/<int:book_id>/', score.ScoreAdd.as_view(), name='add-score'),
    path('score-update/<int:book_id>/', score.ScoreUpdate.as_view(), name='update-score'),
    path('score-delete/<int:book_id>/', score.ScoreDelete.as_view(), name='delete-score'),
]
"""
Defines URL patterns for the book score management API endpoints.

    - URL: `score-add/<int:book_id>/`
    - The `book_id` is a path parameter that specifies the ID of the book for which the score is being added.
    - Maps to the `ScoreAdd` view class from `apps.book.views.score`.
    - The `name='add-score'` provides a name to reference this URL pattern in Django templates and views.

    - URL: `score-update/<int:book_id>/`
    - The `book_id` is a path parameter that specifies the ID of the book for which the score is being updated.
    - Maps to the `ScoreUpdate` view class from `apps.book.views.score`.
    - The `name='update-score'` provides a name to reference this URL pattern in Django templates and views.

    - URL: `score-delete/<int:book_id>/`
    - The `book_id` is a path parameter that specifies the ID of the book for which the score is being deleted.
    - Maps to the `ScoreDelete` view class from `apps.book.views.score`.
    - The `name='delete-score'` provides a name to reference this URL pattern in Django templates and views.
"""
