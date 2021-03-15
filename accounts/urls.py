from django.urls import path, include
from django.conf.urls import url
from . import views
app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_request/', views.password_reset_request, name="password_reset_request"),
    path('user_manangement_list/', views.UserManagementList.as_view(), name="user_manangement_list"),
    path('edit_user/<id>/', views.EditUser.as_view(), name="edit_user"),
    path('template_management_list/', views.TemplatesManagementList.as_view(), name="template_management_list"),
    path('delete_temp/<id>/', views.DeleteTemp.as_view(), name='delete_temp'),
    path('delete_u/<id>/', views.DeleteUser.as_view(), name='delete_user'),
    path('delete_colour_set/<id>/', views.DeleteColourSet.as_view(), name='delete_colour_set'),
    path('edit_template/<id>/', views.EditTemplate.as_view(), name='edit_template'),
    path('create_graphic/', views.CreateGraphic.as_view(), name='create_graphic'),
    path('create_color_set/', views.CreateColorSet.as_view(), name='create_color_set'),
    path('edit_color_set/<id>/', views.EditColorSet.as_view(), name='edit_color_set'),
    path('create_templates/', views.CreateTemplate.as_view(), name='create_templates'),
    path('upload_user_csv/', views.UserCsv.as_view(), name='upload_user_csv'),
    path('list_of_colourset/', views.list_of_colourset, name='list_of_colourset'),
    path('create_graph/', views.create_graph, name='create_graph'),
    path('generate_code/', views.generate_code, name='generate_code'),

]
