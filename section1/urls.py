from django.urls import path

from .views import (QuarterListView, QuarterDetailView, QuarterCreateView, QuarterUpdateView, QuarterDeleteView, \
                    MonthListView, MonthCreateView, MonthUpdateView, MonthDeleteView, \
                    FamilyListView, FamilyCreateView, FamilyUpdateView, FamilyDeleteView, \
                    AdultListView, AdultCreateView, AdultUpdateView, AdultDeleteView, \
                    ChildListView, ChildCreateView, ChildUpdateView, ChildDeleteView, \
                    ValidateDataView, ErrorListView, FileUploadView, ProcessQuarterView)

urlpatterns = [
    path("quarters/", QuarterListView.as_view(), name="quarter-list"),
    #path("<int:pk>/", QuarterDetailView.as_view(), name="quarter_detail"),
    path("quarter/new/", QuarterCreateView.as_view(), name="quarter-create"),
    path("quarter/update/<int:pk>/", QuarterUpdateView.as_view(), name="quarter-update"),
    path("quarter/delete/<int:pk>/", QuarterDeleteView.as_view(), name="quarter-delete"),

    #path("quarter/<int:pk>/<str:report_quarter>/months/", MonthListView.as_view(), name="month-list"),
    path('quarters/<int:quarter_pk>/months/', MonthListView.as_view(), name='month-list'),
    #path("<int:pk>/", QuarterDetailView.as_view(), name="quarter_detail"),
    #path("quarter/<str:report_quarter>/month/new/", MonthCreateView.as_view(), name="month-create"),
    path('quarter/<int:quarter_pk>/month/create/', MonthCreateView.as_view(), name='month_create'),
    path("month/update/<int:pk>/", MonthUpdateView.as_view(), name="month-update"),
    path("month/delete/<int:pk>/", MonthDeleteView.as_view(), name="month-delete"),

    path('month/<int:month_id>/families/', FamilyListView.as_view(), name='family_list'),
    #path('families/', FamilyListView.as_view(), name='family_list'),
    path('month/<int:month_id>/family/create/', FamilyCreateView.as_view(), name='family_create'),
    #path('family/<int:pk>/', FamilyDetailView.as_view(), name='family_detail'),
    path('family/<int:pk>/update/', FamilyUpdateView.as_view(), name='family_update'),
    path('family/<int:pk>/delete/', FamilyDeleteView.as_view(), name='family_delete'),

    path('family/<int:family_id>/adults/', AdultListView.as_view(), name='adult_list'),
    path('family/<int:family_id>/adult/create/', AdultCreateView.as_view(), name='adult_create'),
    #path('family/<int:pk>/', FamilyDetailView.as_view(), name='family_detail'),
    path('family/<int:id>/adult/<int:pk>/update/', AdultUpdateView.as_view(), name='adult_update'),
    path('family/<int:family_id>/adult/<int:pk>/delete/', AdultDeleteView.as_view(), name='adult_delete'),

    path('family/<int:family_id>/children/', ChildListView.as_view(), name='child_list'),
    path('family/<int:family_id>/child/create/', ChildCreateView.as_view(), name='child_create'),
    #path('family/<int:pk>/', FamilyDetailView.as_view(), name='family_detail'),
    path('family/<int:id>/child/<int:pk>/update/', ChildUpdateView.as_view(), name='child_update'),
    path('family/<int:family_id>/child/<int:pk>/delete/', ChildDeleteView.as_view(), name='child_delete'),

    path('validations/', ValidateDataView.as_view(), name='validate_data'),
    path('validations/<int:month>/version/<int:version>/errors/', ErrorListView.as_view(), name='error_list'),

    path('upload/<int:month_id>/', FileUploadView.as_view(), name='file_upload'),

    path('createfile/', ProcessQuarterView.as_view(), name='create_file'),
    #path('files/', ListFilesView.as_view(), name='list_files'),
]