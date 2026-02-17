from django.urls import path , re_path
from . import views
from django.views.generic import TemplateView

app_name='core'

urlpatterns = [
    path("",views.index, name="home"),
    path("machaoui-ilyes-oran/", views.index, name="machaoui_seo"),

    path("latest-order-meta/", views.latest_order_meta, name="latest_order_meta"),
    path("submit-form/",views.submit_feedback,name="submit_form"),
    re_path(r'^sitemap\.xml$', TemplateView.as_view(
        template_name="sitemap.xml",
        content_type="application/xml"
    )),
]
