from django.urls import path
from . import views

app_name='core'

urlpatterns = [
    path("",views.index, name="home"),
    path("machaoui-ilyes-oran/", views.index, name="machaoui_seo"),

    path("latest-order-meta/", views.latest_order_meta, name="latest_order_meta"),
    path("submit-form/",views.submit_feedback,name="submit_form"),

]
