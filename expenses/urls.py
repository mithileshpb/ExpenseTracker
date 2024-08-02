from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'expenses', views.ExpenseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('today/',views.today),
    path('export-expenses/', views.export_expenses),
    path('export-expenses-pdf/', views.export_expenses_pdf),
    path('one-week/', views.oneWeek),
    path('15days/', views.last15Days),
    path('custom-dates/', views.customDates),
]